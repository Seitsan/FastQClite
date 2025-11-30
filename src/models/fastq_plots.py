from pathlib import Path
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import numpy as np
from .fastq_reader import FastqReader

plt.style.use('default')


def run_analysis(file_path: str | Path) -> Dict[str, Any]:
    """
    Анализирует FASTQ-файл и собирает ключевые метрики качества последовательностей.

    Args:
        file_path (str | Path): Путь к FASTQ-файлу.

    Returns:
        Dict[str, Any]: Словарь с собранными данными для построения графиков.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    if file_path.stat().st_size == 0:
        raise RuntimeError("Файл пуст.")

    sequence_lengths: List[int] = []
    quality_per_position: Dict[int, List[int]] = {}
    base_content_per_position: Dict[int, Dict[str, int]] = {}  # pos -> {A: N, T: N, ...}

    total_sequences = 0

    with FastqReader(file_path) as reader:
        for record in reader.read():
            seq = record.sequence
            qual = record.quality
            seq_len = len(seq)

            total_sequences += 1
            sequence_lengths.append(seq_len)

            # Сбор качества по позициям
            for i, q in enumerate(qual):
                if i not in quality_per_position:
                    quality_per_position[i] = []
                quality_per_position[i].append(q)

            # Сбор содержания оснований по позициям
            for i, base in enumerate(seq):
                if i not in base_content_per_position:
                    base_content_per_position[i] = {"A": 0, "T": 0, "G": 0, "C": 0}
                if base in "ATGC":
                    base_content_per_position[i][base] += 1

    if total_sequences == 0:
        raise RuntimeError("В файле не найдено действительных последовательностей.")

    # 1. Расчет среднего качества
    mean_qualities_data = None
    if quality_per_position:
        positions = sorted(quality_per_position.keys())
        mean_qualities_data = {
            'positions': positions,
            'mean_qualities': [np.mean(quality_per_position[p]) for p in positions]
        }

    # 2. Расчет процентного содержания нуклеотидов
    base_content_data = None
    if base_content_per_position:
        positions = sorted(base_content_per_position.keys())
        base_content_data = {'A': [], 'T': [], 'G': [], 'C': [], 'positions': positions}

        for p in positions:
            counts = base_content_per_position[p]
            total_at_pos = sum(counts.values())

            if total_at_pos > 0:
                for base in ['A', 'T', 'G', 'C']:
                    base_content_data[base].append(counts.get(base, 0) / total_at_pos * 100)
            else:
                for base in ['A', 'T', 'G', 'C']:
                    base_content_data[base].append(0)

    return {
        'sequence_lengths': sequence_lengths,
        'mean_qualities_data': mean_qualities_data,
        'base_content_data': base_content_data
    }


def create_figure_length(data: List[int], accent_color: str) -> plt.Figure:
    """Строит график распределения длин последовательностей."""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

    if data:
        bins = min(50, len(set(data))) if len(data) > 1 else 1
        ax.hist(data, bins=bins,
                color=accent_color,
                edgecolor='white',
                alpha=0.7)
        ax.set_title("Распределение длин последовательностей", fontsize=12)
        ax.set_xlabel("Длина последовательности (п.н.)", fontsize=10)
        ax.set_ylabel("Частота", fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
    else:
        ax.text(0.5, 0.5, "Данные о длине отсутствуют",
                ha='center', va='center', fontsize=12)

    fig.tight_layout()
    return fig


def create_figure_quality(data: Dict[str, Any], accent_color: str) -> plt.Figure:
    """Строит график среднего качества по каждой позиции."""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

    if data and data['positions']:
        positions = data['positions']
        mean_qualities = data['mean_qualities']

        ax.plot(positions, mean_qualities, color=accent_color, linewidth=2, label='Среднее качество')
        ax.axhline(y=20, color='red', linestyle='--', alpha=0.7, label='Q20')
        ax.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Q30')

        ax.set_title("Среднее качество по каждой позиции в риде", fontsize=12)
        ax.set_xlabel("Позиция в риде (п.н.)", fontsize=10)
        ax.set_ylabel("Phred Quality Score", fontsize=10)
        ax.legend(fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Данные о качестве отсутствуют",
                ha='center', va='center', fontsize=12)

    fig.tight_layout()
    return fig


def create_figure_content(data: Dict[str, Any], accent_color: str) -> plt.Figure:
    """Строит график процентного содержания нуклеотидов по позициям."""
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)

    if data and data['positions']:
        positions = data['positions']

        # Используем стандартные цвета для нуклеотидов
        ax.plot(positions, data['A'], label='A', color='green', linewidth=1.5)
        ax.plot(positions, data['T'], label='T', color='red', linewidth=1.5)
        ax.plot(positions, data['G'], label='G', color='orange', linewidth=1.5)
        ax.plot(positions, data['C'], label='C', color='blue', linewidth=1.5)

        # Горизонтальная линия для 25% (равное распределение)
        ax.axhline(y=25, color='black', linestyle=':', alpha=0.5, linewidth=0.8)

        ax.set_title("Процентное содержание каждого нуклеотида по позициям", fontsize=12)
        ax.set_xlabel("Позиция в риде (п.н.)", fontsize=10)
        ax.set_ylabel("Процент (%)", fontsize=10)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, linestyle='--', alpha=0.3)
    else:
        ax.text(0.5, 0.5, "Данные о нуклеотидном составе отсутствуют",
                ha='center', va='center', fontsize=12)

    fig.tight_layout()
    return fig
