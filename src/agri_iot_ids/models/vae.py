from __future__ import annotations

import torch
from torch import nn


class VariationalAutoencoder(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int = 16, hidden_dims: list[int] | None = None):
        super().__init__()
        hidden_dims = hidden_dims or [128, 64]

        encoder_layers: list[nn.Module] = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU()])
            prev_dim = hidden_dim

        self.encoder = nn.Sequential(*encoder_layers)
        self.mu_head = nn.Linear(prev_dim, latent_dim)
        self.logvar_head = nn.Linear(prev_dim, latent_dim)

        decoder_layers: list[nn.Module] = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([nn.Linear(prev_dim, hidden_dim), nn.ReLU()])
            prev_dim = hidden_dim
        decoder_layers.append(nn.Linear(prev_dim, input_dim))
        self.decoder = nn.Sequential(*decoder_layers)

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        encoded = self.encoder(x)
        mu = self.mu_head(encoded)
        logvar = self.logvar_head(encoded)
        latent = self.reparameterize(mu, logvar)
        reconstruction = self.decoder(latent)
        return reconstruction, mu, logvar, latent

