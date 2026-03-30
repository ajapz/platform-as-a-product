from __future__ import annotations

from pathlib import Path
from typing import Iterable

import click
import yaml
from rich.console import Console

console = Console()


def _iter_yaml_files(path: Path) -> Iterable[Path]:
    if path.is_file() and path.suffix in {".yaml", ".yml"}:
        yield path
        return

    for candidate in sorted(path.rglob("*.y*ml")):
        if candidate.is_file():
            yield candidate


def _load_yaml_documents(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        docs = [doc for doc in yaml.safe_load_all(handle) if doc]
    return [doc for doc in docs if isinstance(doc, dict)]


def _baseline_netpol_docs(namespace: str) -> list[dict]:
    return [
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "default-deny-all", "namespace": namespace},
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
            },
        },
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "allow-dns-egress", "namespace": namespace},
            "spec": {
                "podSelector": {},
                "policyTypes": ["Egress"],
                "egress": [
                    {
                        "to": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "kubernetes.io/metadata.name": "kube-system"
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 53},
                        ],
                    }
                ],
            },
        },
        {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "allow-from-istio-ingress",
                "namespace": namespace,
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress"],
                "ingress": [
                    {
                        "from": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "kubernetes.io/metadata.name": "istio-system"
                                    }
                                }
                            }
                        ]
                    }
                ],
            },
        },
    ]


def _extract_namespaces_from_file(namespaces_file: Path) -> list[str]:
    names: list[str] = []
    for doc in _load_yaml_documents(namespaces_file):
        if doc.get("kind") != "Namespace":
            continue
        name = doc.get("metadata", {}).get("name")
        if isinstance(name, str) and name:
            names.append(name)
    return names


def _labels_match(selector: dict, labels: dict) -> bool:
    if not selector:
        return False
    match_labels = selector.get("matchLabels", {})
    match_expressions = selector.get("matchExpressions", [])

    labels_match = all(labels.get(key) == value for key, value in match_labels.items())

    expressions_match = True
    for expr in match_expressions:
        key = expr.get("key")
        op = expr.get("operator")
        values = expr.get("values", [])
        label_value = labels.get(key)

        if op == "In" and label_value not in values:
            expressions_match = False
        elif op == "NotIn" and label_value in values:
            expressions_match = False
        elif op == "Exists" and key not in labels:
            expressions_match = False
        elif op == "DoesNotExist" and key in labels:
            expressions_match = False

    return labels_match and expressions_match and (bool(match_labels) or bool(match_expressions))


@click.group()
def cli() -> None:
    """Platform engineering automation CLI."""


@cli.command("validate-manifests")
@click.argument("target", type=click.Path(exists=True, path_type=Path))
def validate_manifests(target: Path) -> None:
    """Validate common Kubernetes manifest requirements."""
    failures: list[str] = []
    checked = 0

    for yaml_file in _iter_yaml_files(target):
        checked += 1
        for idx, doc in enumerate(_load_yaml_documents(yaml_file), start=1):
            kind = doc.get("kind")
            api_version = doc.get("apiVersion")
            metadata = doc.get("metadata", {})
            name = metadata.get("name")

            if not kind or not api_version:
                failures.append(f"{yaml_file}: doc {idx} missing kind/apiVersion")
            if not name:
                failures.append(f"{yaml_file}: doc {idx} missing metadata.name")

            if kind == "Deployment":
                spec = doc.get("spec", {})
                replicas = spec.get("replicas", 1)
                pod_spec = spec.get("template", {}).get("spec", {})
                pod_security = pod_spec.get("securityContext", {})
                if replicas < 2:
                    failures.append(
                        f"{yaml_file}: doc {idx} deployment replicas should be >= 2"
                    )

                if pod_security.get("runAsNonRoot") is not True:
                    failures.append(
                        f"{yaml_file}: doc {idx} deployment must set pod securityContext.runAsNonRoot=true"
                    )

                containers = pod_spec.get("containers", [])
                if not containers:
                    failures.append(
                        f"{yaml_file}: doc {idx} deployment has no containers defined"
                    )

                for container in containers:
                    cname = container.get("name", "unnamed")
                    image = container.get("image", "")
                    resources = container.get("resources", {})
                    limits = resources.get("limits", {})
                    requests = resources.get("requests", {})
                    sec = container.get("securityContext", {})

                    if ":latest" in image:
                        failures.append(
                            f"{yaml_file}: doc {idx} container {cname} must not use latest image tag"
                        )

                    if not limits.get("cpu") or not limits.get("memory"):
                        failures.append(
                            f"{yaml_file}: doc {idx} container {cname} missing resource limits"
                        )
                    if not requests.get("cpu") or not requests.get("memory"):
                        failures.append(
                            f"{yaml_file}: doc {idx} container {cname} missing resource requests"
                        )

                    if sec.get("allowPrivilegeEscalation") is not False:
                        failures.append(
                            f"{yaml_file}: doc {idx} container {cname} must set allowPrivilegeEscalation=false"
                        )
                    if sec.get("readOnlyRootFilesystem") is not True:
                        failures.append(
                            f"{yaml_file}: doc {idx} container {cname} must set readOnlyRootFilesystem=true"
                        )

    if failures:
        console.print("[red]Manifest validation failed:[/red]")
        for failure in failures:
            console.print(f"- {failure}")
        raise SystemExit(1)

    console.print(
        f"[green]Manifest validation passed.[/green] Checked {checked} YAML files."
    )


@cli.command("generate-baseline-netpol")
@click.argument("namespace")
@click.option(
    "--output",
    default="network-policy.yaml",
    show_default=True,
    type=click.Path(path_type=Path),
)
def generate_baseline_netpol(namespace: str, output: Path) -> None:
    """Generate a default-deny plus DNS egress network policy baseline."""
    docs = _baseline_netpol_docs(namespace)

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        yaml.safe_dump_all(docs, handle, sort_keys=False)

    console.print(f"[green]Generated baseline network policies in {output}[/green]")


@cli.command("generate-netpol-bundle")
@click.option(
    "--namespace",
    "namespaces",
    multiple=True,
    help="Namespace to generate policy for. Repeat the flag for multiple namespaces.",
)
@click.option(
    "--namespaces-file",
    type=click.Path(exists=True, path_type=Path),
    help="YAML file containing Namespace resources to derive namespaces from.",
)
@click.option(
    "--output-dir",
    default="network-policies",
    show_default=True,
    type=click.Path(path_type=Path),
)
def generate_netpol_bundle(
    namespaces: tuple[str, ...], namespaces_file: Path | None, output_dir: Path
) -> None:
    """Generate baseline network policy files for multiple namespaces."""
    target_namespaces = set(namespaces)
    if namespaces_file:
        target_namespaces.update(_extract_namespaces_from_file(namespaces_file))

    if not target_namespaces:
        raise click.ClickException(
            "Provide at least one --namespace or a --namespaces-file containing Namespace objects."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    for namespace in sorted(target_namespaces):
        docs = _baseline_netpol_docs(namespace)
        output_path = output_dir / f"{namespace}-baseline.yaml"
        with output_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump_all(docs, handle, sort_keys=False)

    console.print(
        f"[green]Generated baseline network policy bundle for {len(target_namespaces)} namespaces in {output_dir}[/green]"
    )


@cli.command("check-ha")
@click.argument("target", type=click.Path(exists=True, path_type=Path))
def check_ha(target: Path) -> None:
    """Check if critical HA patterns are present in workload specs."""
    warnings: list[str] = []
    all_docs: list[tuple[Path, int, dict]] = []

    for yaml_file in _iter_yaml_files(target):
        for idx, doc in enumerate(_load_yaml_documents(yaml_file), start=1):
            all_docs.append((yaml_file, idx, doc))

    hpa_targets: set[tuple[str, str]] = set()
    pdb_selectors: dict[str, list[dict]] = {}
    deployments = 0

    for _, _, doc in all_docs:
        metadata = doc.get("metadata", {})
        namespace = metadata.get("namespace", "default")
        kind = doc.get("kind")

        if kind == "HorizontalPodAutoscaler":
            ref = doc.get("spec", {}).get("scaleTargetRef", {})
            if ref.get("kind") == "Deployment" and ref.get("name"):
                hpa_targets.add((namespace, ref["name"]))

        if kind == "PodDisruptionBudget":
            selector = doc.get("spec", {}).get("selector", {})
            spec = doc.get("spec", {})
            min_available = spec.get("minAvailable")
            max_unavailable = spec.get("maxUnavailable")
            if min_available is None and max_unavailable is None:
                warnings.append(
                    f"PDB {metadata.get('name', 'unknown')} in namespace {namespace} must define minAvailable or maxUnavailable"
                )
            pdb_selectors.setdefault(namespace, []).append(selector)

    for yaml_file, idx, doc in all_docs:
        if doc.get("kind") != "Deployment":
            continue

        deployments += 1
        metadata = doc.get("metadata", {})
        deployment_name = metadata.get("name", "unknown")
        namespace = metadata.get("namespace", "default")
        spec = doc.get("spec", {})
        pod_spec = spec.get("template", {}).get("spec", {})
        template_labels = spec.get("template", {}).get("metadata", {}).get("labels", {})
        containers = pod_spec.get("containers", [])

        if spec.get("replicas", 1) < 2:
            warnings.append(f"{yaml_file}: doc {idx} replicas below HA target")
        if not pod_spec.get("affinity"):
            warnings.append(f"{yaml_file}: doc {idx} missing pod affinity/anti-affinity")
        if not pod_spec.get("topologySpreadConstraints"):
            warnings.append(f"{yaml_file}: doc {idx} missing topology spread constraints")

        if not containers:
            warnings.append(f"{yaml_file}: doc {idx} deployment has no containers defined")
        for container in containers:
            container_name = container.get("name", "unnamed")
            image = container.get("image", "")
            resources = container.get("resources", {})
            requests = resources.get("requests", {})
            limits = resources.get("limits", {})
            if "readinessProbe" not in container:
                warnings.append(
                    f"{yaml_file}: doc {idx} container {container_name} missing readinessProbe"
                )
            if "livenessProbe" not in container:
                warnings.append(
                    f"{yaml_file}: doc {idx} container {container_name} missing livenessProbe"
                )
            if ":latest" in image:
                warnings.append(
                    f"{yaml_file}: doc {idx} container {container_name} uses latest image tag"
                )
            if not requests.get("cpu") or not requests.get("memory"):
                warnings.append(
                    f"{yaml_file}: doc {idx} container {container_name} missing resource requests"
                )
            if not limits.get("cpu") or not limits.get("memory"):
                warnings.append(
                    f"{yaml_file}: doc {idx} container {container_name} missing resource limits"
                )

        if (namespace, deployment_name) not in hpa_targets:
            warnings.append(
                f"{yaml_file}: doc {idx} deployment {deployment_name} missing matching HPA"
            )

        namespace_pdbs = pdb_selectors.get(namespace, [])
        has_matching_pdb = any(_labels_match(selector, template_labels) for selector in namespace_pdbs)
        if not has_matching_pdb:
            warnings.append(
                f"{yaml_file}: doc {idx} deployment {deployment_name} missing matching PDB selector"
            )

    if warnings:
        console.print("[yellow]HA check found gaps:[/yellow]")
        for warning in warnings:
            console.print(f"- {warning}")
        raise SystemExit(1)

    console.print(
        f"[green]HA check passed.[/green] Checked {deployments} deployment resources."
    )


if __name__ == "__main__":
    cli()
