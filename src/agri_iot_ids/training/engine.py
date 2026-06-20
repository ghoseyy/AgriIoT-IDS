from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import average_precision_score, f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def build_loader(array: np.ndarray, batch_size: int, shuffle: bool) -> DataLoader:
    tensor = torch.from_numpy(array)
    dataset = TensorDataset(tensor)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def autoencoder_loss(reconstruction: torch.Tensor, inputs: torch.Tensor) -> torch.Tensor:
    return nn.functional.mse_loss(reconstruction, inputs)


def vae_loss(
    reconstruction: torch.Tensor,
    inputs: torch.Tensor,
    mu: torch.Tensor,
    logvar: torch.Tensor,
    beta: float = 1.0,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    recon_loss = nn.functional.mse_loss(reconstruction, inputs)
    kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
    total_loss = recon_loss + beta * kl_loss
    return total_loss, recon_loss, kl_loss


def fit_autoencoder(
    model: torch.nn.Module,
    train_array: np.ndarray,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    device: str,
    verbose: bool = False,
) -> list[dict[str, float]]:
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loader = build_loader(train_array, batch_size=batch_size, shuffle=True)
    history: list[dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        for (batch,) in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            reconstruction, _ = model(batch)
            loss = autoencoder_loss(reconstruction, batch)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * len(batch)

        epoch_metrics = {"epoch": epoch, "train_loss": running_loss / len(train_array)}
        history.append(epoch_metrics)
        if verbose:
            print(f"epoch={epoch} train_loss={epoch_metrics['train_loss']:.6f}", flush=True)

    return history


def fit_vae(
    model: torch.nn.Module,
    train_array: np.ndarray,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    beta: float,
    device: str,
    verbose: bool = False,
) -> list[dict[str, float]]:
    model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loader = build_loader(train_array, batch_size=batch_size, shuffle=True)
    history: list[dict[str, float]] = []

    for epoch in range(1, epochs + 1):
        model.train()
        total_running = 0.0
        recon_running = 0.0
        kl_running = 0.0

        for (batch,) in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            reconstruction, mu, logvar, _ = model(batch)
            total_loss, recon_loss, kl_loss = vae_loss(reconstruction, batch, mu, logvar, beta=beta)
            total_loss.backward()
            optimizer.step()

            total_running += total_loss.item() * len(batch)
            recon_running += recon_loss.item() * len(batch)
            kl_running += kl_loss.item() * len(batch)

        epoch_metrics = {
            "epoch": epoch,
            "train_loss": total_running / len(train_array),
            "recon_loss": recon_running / len(train_array),
            "kl_loss": kl_running / len(train_array),
        }
        history.append(epoch_metrics)
        if verbose:
            print(
                "epoch={epoch} train_loss={train_loss:.6f} recon_loss={recon_loss:.6f} kl_loss={kl_loss:.6f}".format(
                    **epoch_metrics
                ),
                flush=True,
            )

    return history


def score_autoencoder(model: torch.nn.Module, array: np.ndarray, device: str, batch_size: int = 8192) -> np.ndarray:
    model.eval()
    model.to(device)
    scores = []
    loader = build_loader(array, batch_size=batch_size, shuffle=False)
    with torch.no_grad():
        for (batch,) in loader:
            inputs = batch.to(device)
            reconstruction, _ = model(inputs)
            errors = torch.mean((reconstruction - inputs) ** 2, dim=1)
            scores.append(errors.detach().cpu().numpy())
    return np.concatenate(scores)


def score_vae(model: torch.nn.Module, array: np.ndarray, device: str, batch_size: int = 8192) -> np.ndarray:
    model.eval()
    model.to(device)
    scores = []
    loader = build_loader(array, batch_size=batch_size, shuffle=False)
    with torch.no_grad():
        for (batch,) in loader:
            inputs = batch.to(device)
            reconstruction, _, _, _ = model(inputs)
            errors = torch.mean((reconstruction - inputs) ** 2, dim=1)
            scores.append(errors.detach().cpu().numpy())
    return np.concatenate(scores)


def select_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(labels, scores)
    if len(thresholds) == 0:
        return float(np.max(scores))

    precision = precision[:-1]
    recall = recall[:-1]
    f1 = np.divide(
        2 * precision * recall,
        precision + recall,
        out=np.zeros_like(precision),
        where=(precision + recall) > 0,
    )
    return float(thresholds[int(np.argmax(f1))])


def evaluate_scores(scores: np.ndarray, labels: np.ndarray, threshold: float) -> dict[str, float]:
    predictions = (scores >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(labels, scores)),
        "pr_auc": float(average_precision_score(labels, scores)),
    }


def save_json(payload: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
