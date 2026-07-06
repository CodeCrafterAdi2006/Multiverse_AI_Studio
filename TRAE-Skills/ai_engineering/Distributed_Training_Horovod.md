# Skill: Distributed Training (Horovod)

## Purpose
To train large machine learning models faster by distributing the computational workload across multiple GPUs or nodes, using data parallelism or model parallelism techniques. Horovod (by Uber) provides a simple and efficient framework for distributed deep learning.

## When to Use
- When training large models (e.g., Transformers, high-res CNNs) that exceed a single GPU's memory or take too long to converge
- When scaling out training to a cluster of machines
- When utilizing multi-GPU instances in the cloud (AWS p4d, GCP A100)
- When migrating single-GPU PyTorch or TensorFlow code to multi-GPU without extensive rewrites

## Procedure

### 1. Installation
Install Horovod with the necessary framework support (PyTorch, TensorFlow, etc.).
```bash
# Requires MPI (Message Passing Interface) installed on the system
HOROVOD_WITH_PYTORCH=1 pip install horovod[pytorch]
```

### 2. PyTorch Integration Example
Convert a standard PyTorch training script to a distributed one.

**Initialize Horovod**:
```python
import torch
import horovod.torch as hvd

# 1. Initialize Horovod
hvd.init()

# 2. Pin GPU to local rank (ensure each process uses a different GPU)
if torch.cuda.is_available():
    torch.cuda.set_device(hvd.local_rank())
```

**Data Loading**:
Partition the dataset among workers using a `DistributedSampler`.
```python
from torch.utils.data.distributed import DistributedSampler

dataset = MyDataset()
# 3. Partition data
sampler = DistributedSampler(dataset, num_replicas=hvd.size(), rank=hvd.rank())
train_loader = torch.utils.data.DataLoader(dataset, batch_size=32, sampler=sampler)
```

**Optimizer and Broadcasting**:
Scale the learning rate by the number of workers and wrap the optimizer.
```python
model = MyModel().cuda()
# 4. Scale learning rate
optimizer = torch.optim.SGD(model.parameters(), lr=0.01 * hvd.size())

# 5. Add Horovod Distributed Optimizer
optimizer = hvd.DistributedOptimizer(
    optimizer, named_parameters=model.named_parameters(),
    op=hvd.Adsum # Default is hvd.Average
)

# 6. Broadcast initial parameters and optimizer state from rank 0 to all other processes
hvd.broadcast_parameters(model.state_dict(), root_rank=0)
hvd.broadcast_optimizer_state(optimizer, root_rank=0)
```

### 3. Execution
Run the script using `horovodrun` or `mpirun`.

**Local Multi-GPU (e.g., 4 GPUs on one machine)**:
```bash
horovodrun -np 4 -H localhost:4 python train.py
```

**Multi-Node (e.g., 2 machines, 4 GPUs each)**:
```bash
horovodrun -np 8 -H server1:4,server2:4 python train.py
```

## Best Practices
- **Learning Rate Scaling**: Always scale the learning rate linearly with the number of workers (`lr * hvd.size()`), and consider a warmup period for the first few epochs.
- **Checkpointing**: Only save checkpoints on `hvd.rank() == 0` to prevent file corruption from concurrent writes.
- **Batch Size**: The effective batch size becomes `batch_size_per_worker * hvd.size()`. Adjust accordingly to maintain convergence.