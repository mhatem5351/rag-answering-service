SNIPPETS: list[dict] = [
    {
        "id": "k8s_01",
        "title": "Pods",
        "text": (
            "A Pod is the smallest deployable unit in Kubernetes. It encapsulates one or "
            "more containers that share the same network namespace and storage volumes. "
            "Containers within a Pod communicate over localhost and are always co-scheduled "
            "on the same node."
        ),
    },
    {
        "id": "k8s_02",
        "title": "Deployments",
        "text": (
            "A Deployment provides declarative updates for Pods via ReplicaSets. You describe "
            "the desired state and the Deployment controller changes the actual state at a "
            "controlled rate. Rolling updates let you push new container images with zero "
            "downtime by incrementally replacing old Pods."
        ),
    },
    {
        "id": "k8s_03",
        "title": "Services",
        "text": (
            "A Service is a stable networking abstraction that exposes a set of Pods as a "
            "network service. The three main types are ClusterIP (internal only), NodePort "
            "(opens a port on every node), and LoadBalancer (provisions a cloud load balancer). "
            "Services use label selectors to route traffic to the correct Pods."
        ),
    },
    {
        "id": "k8s_04",
        "title": "Namespaces",
        "text": (
            "Namespaces provide logical isolation within a cluster. They let teams share a "
            "cluster while keeping resources separate. You can set per-namespace resource "
            "quotas and limit ranges to prevent one team from starving another of CPU or memory."
        ),
    },
    {
        "id": "k8s_05",
        "title": "ConfigMaps",
        "text": (
            "ConfigMaps decouple configuration from container images. They store key-value "
            "pairs that can be consumed as environment variables, command-line arguments, or "
            "mounted as files inside a Pod. Updating a ConfigMap does not require rebuilding "
            "or redeploying the container image."
        ),
    },
    {
        "id": "k8s_06",
        "title": "Secrets",
        "text": (
            "Secrets are similar to ConfigMaps but designed for sensitive data like passwords, "
            "API tokens, and TLS certificates. They are base64-encoded at rest and can be "
            "mounted as volumes or exposed as environment variables. For stronger security, "
            "enable encryption at rest in etcd."
        ),
    },
    {
        "id": "k8s_07",
        "title": "Persistent Volumes",
        "text": (
            "Persistent Volumes (PVs) decouple storage from the Pod lifecycle. A cluster admin "
            "provisions PVs, and developers claim them with Persistent Volume Claims (PVCs). "
            "This model lets data survive Pod restarts and rescheduling. Storage classes enable "
            "dynamic provisioning from cloud providers."
        ),
    },
    {
        "id": "k8s_08",
        "title": "Horizontal Pod Autoscaler",
        "text": (
            "The Horizontal Pod Autoscaler (HPA) automatically scales the number of Pod replicas "
            "based on observed metrics such as CPU utilization, memory usage, or custom metrics. "
            "It checks metrics at a configurable interval and adjusts the replica count to meet "
            "the target utilization, helping handle traffic spikes efficiently."
        ),
    },
    {
        "id": "k8s_09",
        "title": "Ingress",
        "text": (
            "Ingress manages external HTTP and HTTPS access to Services within a cluster. It "
            "provides URL-based routing, TLS termination, and virtual hosting. An Ingress "
            "controller (like NGINX or Traefik) watches Ingress resources and configures the "
            "underlying load balancer accordingly."
        ),
    },
    {
        "id": "k8s_10",
        "title": "Liveness and Readiness Probes",
        "text": (
            "Liveness probes tell Kubernetes when to restart a container that is stuck or "
            "deadlocked. Readiness probes tell Kubernetes when a container is ready to accept "
            "traffic. Together they prevent routing requests to unhealthy Pods and automatically "
            "recover from failures without manual intervention."
        ),
    },
    {
        "id": "k8s_11",
        "title": "RBAC",
        "text": (
            "Role-Based Access Control (RBAC) regulates access to Kubernetes resources based on "
            "the roles of individual users or service accounts. Roles and ClusterRoles define "
            "permissions, while RoleBindings and ClusterRoleBindings attach those permissions to "
            "subjects. RBAC is essential for multi-tenant cluster security."
        ),
    },
    {
        "id": "k8s_12",
        "title": "Helm",
        "text": (
            "Helm is the package manager for Kubernetes. It uses charts — bundles of templated "
            "YAML manifests — to define, install, and upgrade applications. Values files let you "
            "customize deployments per environment. Helm tracks releases so you can roll back to "
            "a previous version with a single command."
        ),
    },
]
