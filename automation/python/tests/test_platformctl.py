from pathlib import Path

from click.testing import CliRunner

from platform_automation.cli import cli


def test_generate_baseline_netpol_creates_output(tmp_path: Path) -> None:
    output = tmp_path / "netpol.yaml"
    runner = CliRunner()

    result = runner.invoke(
        cli, ["generate-baseline-netpol", "payments-prod", "--output", str(output)]
    )

    assert result.exit_code == 0
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "default-deny-all" in text
    assert "allow-dns-egress" in text


def test_generate_netpol_bundle_for_multiple_namespaces(tmp_path: Path) -> None:
    output_dir = tmp_path / "bundle"
    runner = CliRunner()

    result = runner.invoke(
        cli,
        [
            "generate-netpol-bundle",
            "--namespace",
            "payments-prod",
            "--namespace",
            "search-prod",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    first = output_dir / "payments-prod-baseline.yaml"
    second = output_dir / "search-prod-baseline.yaml"
    assert first.exists()
    assert second.exists()
    assert "allow-from-istio-ingress" in first.read_text(encoding="utf-8")


def test_generate_netpol_bundle_from_namespaces_file(tmp_path: Path) -> None:
    namespaces_file = tmp_path / "namespaces.yaml"
    namespaces_file.write_text(
        """
apiVersion: v1
kind: Namespace
metadata:
  name: payments-dev
---
apiVersion: v1
kind: Namespace
metadata:
  name: search-dev
""".strip(),
        encoding="utf-8",
    )

    output_dir = tmp_path / "bundle"
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "generate-netpol-bundle",
            "--namespaces-file",
            str(namespaces_file),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert (output_dir / "payments-dev-baseline.yaml").exists()
    assert (output_dir / "search-dev-baseline.yaml").exists()


def test_validate_manifests_fails_for_single_replica(tmp_path: Path) -> None:
    manifest = tmp_path / "deployment.yaml"
    manifest.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
        - name: demo
          image: nginx:latest
""".strip(),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifests", str(tmp_path)])

    assert result.exit_code != 0
    assert "replicas should be >= 2" in result.output


def test_check_ha_passes_with_pdb_hpa_and_probes(tmp_path: Path) -> None:
    manifest = tmp_path / "ha.yaml"
    manifest.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
  namespace: payments-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      securityContext:
        runAsNonRoot: true
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: demo
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app: demo
              topologyKey: kubernetes.io/hostname
      containers:
        - name: demo
          image: ghcr.io/example/demo@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
          readinessProbe:
            httpGet:
              path: /healthz
              port: 80
          livenessProbe:
            httpGet:
              path: /livez
              port: 80
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-hpa
  namespace: payments-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: demo-pdb
  namespace: payments-prod
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: demo
""".strip(),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["check-ha", str(tmp_path)])

    assert result.exit_code == 0
    assert "HA check passed" in result.output


def test_check_ha_fails_for_missing_probe_hpa_and_pdb(tmp_path: Path) -> None:
    manifest = tmp_path / "ha-missing.yaml"
    manifest.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
  namespace: payments-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: demo
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app: demo
              topologyKey: kubernetes.io/hostname
      containers:
        - name: demo
          image: nginx:latest
          readinessProbe:
            httpGet:
              path: /healthz
              port: 80
""".strip(),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["check-ha", str(tmp_path)])

    assert result.exit_code != 0
    assert "missing livenessProbe" in result.output
    assert "missing matching HPA" in result.output
    assert "missing matching PDB selector" in result.output


def test_validate_manifests_fails_on_latest_and_missing_security(tmp_path: Path) -> None:
    manifest = tmp_path / "bad-security.yaml"
    manifest.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: insecure
spec:
  replicas: 2
  selector:
    matchLabels:
      app: insecure
  template:
    metadata:
      labels:
        app: insecure
    spec:
      containers:
        - name: insecure
          image: nginx:latest
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
""".strip(),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifests", str(tmp_path)])

    assert result.exit_code != 0
    assert "runAsNonRoot=true" in result.output
    assert "readOnlyRootFilesystem=true" in result.output


def test_check_ha_matches_pdb_with_match_expressions(tmp_path: Path) -> None:
    manifest = tmp_path / "ha-match-expr.yaml"
    manifest.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo
  namespace: payments-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: demo
  template:
    metadata:
      labels:
        app: demo
        tier: api
    spec:
      securityContext:
        runAsNonRoot: true
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: demo
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            - labelSelector:
                matchLabels:
                  app: demo
              topologyKey: kubernetes.io/hostname
      containers:
        - name: demo
          image: ghcr.io/example/demo@sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
          livenessProbe:
            httpGet:
              path: /livez
              port: 8080
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: demo-hpa
  namespace: payments-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: demo
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: demo-pdb
  namespace: payments-prod
spec:
  minAvailable: 2
  selector:
    matchExpressions:
      - key: app
        operator: In
        values: ["demo"]
""".strip(),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["check-ha", str(tmp_path)])

    assert result.exit_code == 0
