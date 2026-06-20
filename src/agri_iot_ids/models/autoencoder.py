from __future__ import annotations

import torch
from torch import nn


class Autoencoder(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 16, hidden_dims: list[int] | None = None):
        super().__init__()
        hidden_dims = hidden_dims or [128, 64]

        encoder_layers: list[nn.Module] = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU()])
            prev_dim = hidden_dim
        encoder_layers.append(nn.Linear(prev_dim, latent_dim))

        decoder_layers: list[nn.Module] = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU()])
            prev_dim = hidden_dim
        decoder_layers.append(nn.Linear(prev_dim, input_dim))

        self.encoder = nn.Sequential(*encoder_layers)
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction, latent

