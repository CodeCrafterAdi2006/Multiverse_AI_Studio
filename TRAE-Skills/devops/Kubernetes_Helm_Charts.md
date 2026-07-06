# Skill: Kubernetes Helm Charts

## Purpose
To package, deploy, and manage Kubernetes applications using Helm charts.

## When to Use
- When deploying complex applications to Kubernetes
- For managing multiple environments (dev, staging, prod)
- When sharing applications with others
- For versioning and rolling back application deployments
- When you need reusable application templates

## Procedure

### 1. Create a Helm Chart
Scaffold a new Helm chart.

```bash
# Create a new chart
helm create myapp

# Explore the chart structure
cd myapp
ls -la
```

### 2. Chart Structure
Understand the Helm chart structure.

```
myapp/
├── Chart.yaml          # Chart metadata
├── values.yaml         # Default configuration values
├── charts/             # Dependency charts
├── templates/          # Kubernetes manifest templates
│   ├── NOTES.txt       # Usage notes
│   ├── _helpers.tpl    # Template helpers
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── tests/
└── .helmignore         # Files to ignore
```

### 3. Chart.yaml
Define chart metadata.

```yaml
apiVersion: v2
name: myapp
description: A Helm chart for my application
type: application
version: 0.1.0
appVersion: "1.0.0"
keywords:
  - myapp
  - web
maintainers:
  - name: Your Name
    email: your.email@example.com
```

### 4. values.yaml
Define default configuration values.

```yaml
replicaCount: 3

image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: "1.25.0"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}
podSecurityContext: {}

securityContext: {}

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []

resources:
  limits:
    cpu: 100m
    memory: 128Mi
  requests:
    cpu: 100m
    memory: 128Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80

nodeSelector: {}
tolerations: []
affinity: {}
```

### 5. Template Deployment
Create Kubernetes manifest templates.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "myapp.fullname" . }}
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "myapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "myapp.labels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "myapp.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /
              port: http
          readinessProbe:
            httpGet:
              path: /
              port: http
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### 6. Deploy the Chart
Install and manage the chart.

```bash
# Install the chart
helm install myapp ./myapp

# Install with custom values
helm install myapp ./myapp -f values-production.yaml

# Install with set values
helm install myapp ./myapp --set replicaCount=5,image.tag=1.26.0

# List releases
helm list

# Upgrade the release
helm upgrade myapp ./myapp --set image.tag=1.27.0

# Rollback to previous version
helm rollback myapp

# Uninstall the release
helm uninstall myapp

# Template the chart (render manifests without installing)
helm template myapp ./myapp

# Lint the chart
helm lint ./myapp
```

### 7. Environment-Specific Values
Create values files for different environments.

```yaml
# values-dev.yaml
replicaCount: 1
ingress:
  enabled: true
  hosts:
    - host: dev.myapp.com
      paths:
        - path: /
          pathType: ImplementationSpecific

# values-staging.yaml
replicaCount: 2
ingress:
  enabled: true
  hosts:
    - host: staging.myapp.com
      paths:
        - path: /
          pathType: ImplementationSpecific

# values-prod.yaml
replicaCount: 5
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
ingress:
  enabled: true
  hosts:
    - host: myapp.com
      paths:
        - path: /
          pathType: ImplementationSpecific
```

## Best Practices
- **Semantic Versioning**: Follow semantic versioning for charts
- **Default Values**: Provide sensible defaults in values.yaml
- **Documentation**: Document all values in values.yaml comments
- **Template Helpers**: Use _helpers.tpl for reusable template functions
- **Testing**: Write chart tests in the templates/tests directory
- **Dependencies**: Declare dependencies in Chart.yaml
- **Security**: Use least-privilege security contexts
- **Linting**: Always lint charts before deployment
