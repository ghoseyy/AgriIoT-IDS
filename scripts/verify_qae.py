"""Quick sanity check: forward + backward pass through QuantumAutoencoder."""
import torch

from agri_iot_ids.models.qae import QuantumAutoencoder

device = torch.device("cpu")
model = QuantumAutoencoder(input_dim=10, latent_dim=4, n_qubits=4).to(device)
x = torch.randn(8, 10).to(device)

# forward
recon, latent = model(x)
assert recon.shape == (8, 10), f"recon shape mismatch: {recon.shape}"
assert latent.shape == (8, 4), f"latent shape mismatch: {latent.shape}"

# backward (MSE loss)
loss = torch.nn.functional.mse_loss(recon, x)
loss.backward()

# check gradients flowed
n_learnable = sum(1 for p in model.parameters() if p.grad is not None)
print(f"Forward/backward OK  |  params with gradients: {n_learnable}")
print(f"Reconstruction loss : {loss.item():.6f}")
print(f"Quantum weights grad: {model.quantum_layer.weights.grad.norm():.6f}")
print("QAE verified.")
