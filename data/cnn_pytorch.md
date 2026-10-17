# CNN image classifier with PyTorch (MNIST)

A small convolutional network for 28x28 grayscale images with 10 classes.
Needs `pip install torch torchvision`.

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms


class CNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),                  # 28 -> 14
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),                  # 14 -> 7
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(32 * 7 * 7, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x))


def train(epochs=3):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data = datasets.MNIST("data", train=True, download=True, transform=transforms.ToTensor())
    loader = DataLoader(data, batch_size=64, shuffle=True)

    model = CNN().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        total = 0
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = loss_fn(model(images), labels)
            loss.backward()
            optimizer.step()
            total += loss.item()
        print(f"epoch {epoch + 1}, loss {total / len(loader):.4f}")
    return model


if __name__ == "__main__":
    train()
```
