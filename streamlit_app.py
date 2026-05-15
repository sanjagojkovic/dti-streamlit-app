import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams['font.family'] = 'DejaVu Sans'

st.set_page_config(
    page_title="Графички приказ",
    layout="wide"
)

st.title("Графички приказ")

uploaded_file = st.file_uploader(
    "Учитај Excel фајл",
    type=["xlsx"]
)

if uploaded_file is not None:

    raw_df = pd.read_excel("Rezultati.xlsx")

    raw_df.columns = raw_df.columns.str.strip()
    raw_df['Group'] = raw_df['Group'].str.strip()

    params = ['FA', 'MD', 'AD', 'RD']

    prikaz = st.selectbox(
        "Избор приказа",
        [
            "scatter",
            "boxplot",
            "bar",
            "error bar plot",
            "doughnut",
            "radar chart",
            "histogram"
        ]
    )

    # =====================================================
    # SCATTER
    # =====================================================

    if prikaz == "scatter":

        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        for i, p in enumerate(params):

            ax = axes.flatten()[i]

            for group, color, label in zip(
                    ['Patients', 'Volunteers'],
                    ['#e74c3c', '#3498db'],
                    ['Пацијенти', 'Волонтери']):

                subset = raw_df[raw_df['Group'] == group]

                ax.scatter(
                    subset['Subject'],
                    subset[p],
                    c=color,
                    label=label,
                    alpha=0.7
                )

            ax.set_title(p, fontweight='bold')

            ax.tick_params(
                axis='x',
                rotation=90,
                labelsize=7
            )

            ax.legend(prop={'size': 7})

            ax.grid(
                True,
                linestyle='--',
                alpha=0.3
            )

        fig.tight_layout()

        st.pyplot(fig)

    # =====================================================
    # BOXPLOT
    # =====================================================

    elif prikaz == "boxplot":

        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        color_p = '#f5cba7'
        color_v = '#adc2eb'

        for i, p in enumerate(params):

            ax = axes.flatten()[i]

            data_p = raw_df[
                raw_df['Group'] == 'Patients'
            ][p].values

            data_v = raw_df[
                raw_df['Group'] == 'Volunteers'
            ][p].values

            if p in ['MD', 'AD', 'RD']:

                data_p = data_p * 1000
                data_v = data_v * 1000

            bp = ax.boxplot(
                [data_p, data_v],
                widths=0.4,
                patch_artist=True,
                labels=['Patients', 'Volunteers']
            )

            for j, (patch, color) in enumerate(
                    zip(bp['boxes'], [color_p, color_v])):

                patch.set_facecolor(color)
                patch.set_edgecolor('black')
                patch.set_linewidth(0.6)

                c = '#d35400' if j == 0 else '#2980b9'

                bp['whiskers'][2 * j].set(
                    color=c,
                    linestyle=(0, (5, 5)),
                    linewidth=0.8
                )

                bp['whiskers'][2 * j + 1].set(
                    color=c,
                    linestyle=(0, (5, 5)),
                    linewidth=0.8
                )

                bp['medians'][j].set(
                    color=c,
                    linewidth=1
                )

                bp['caps'][2 * j].set(color=c)

                bp['caps'][2 * j + 1].set(color=c)

            ax.set_title(
                f"$\\mathit{{{p}}}$",
                fontsize=12
            )

            y_label = f"$\\mathit{{{p}}}$"

            if p != 'FA':
                y_label += " ($10^{-3}$ mm²/s)"

            ax.set_ylabel(y_label)

            ax.grid(
                True,
                linestyle='-',
                alpha=0.15
            )

            ax.set_facecolor('#fdfdfd')

        fig.tight_layout()

        fig.subplots_adjust(
            top=0.90,
            bottom=0.08,
            hspace=0.3
        )

        legend_elements = [
            Patch(
                facecolor=color_p,
                edgecolor='black',
                label='Пацијенти'
            ),
            Patch(
                facecolor=color_v,
                edgecolor='black',
                label='Волонтери'
            )
        ]

        fig.legend(
            handles=legend_elements,
            loc='upper center',
            ncol=2,
            bbox_to_anchor=(0.5, 1.0),
            frameon=True,
            edgecolor='black',
            fontsize=10,
            borderaxespad=0.2
        )

        st.pyplot(fig)

    # =====================================================
    # BAR
    # =====================================================

    elif prikaz == "bar":

        fig, ax = plt.subplots(figsize=(10, 8))

        all_means = [
            raw_df[p].mean()
            for p in params
        ]

        display_values = [
            all_means[0],
            all_means[1] * 100,
            all_means[2] * 100,
            all_means[3] * 100
        ]

        labels = [
            'FA',
            'MD (x100)',
            'AD (x100)',
            'RD (x100)'
        ]

        moje_boje = [
            '#8e44ad',
            '#ff7f00',
            '#27ae60',
            '#ffff00'
        ]

        bars = ax.bar(
            labels,
            display_values,
            color=moje_boje,
            width=0.7,
            edgecolor='black'
        )

        for bar, real_val in zip(bars, all_means):

            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f'{real_val:.9f}',
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )

        ax.set_title(
            "Средње вриједности DTI параметара",
            fontweight='bold'
        )

        ax.set_ylim(
            0,
            max(display_values) * 1.3
        )

        ax.grid(
            axis='y',
            linestyle=':',
            alpha=0.5
        )

        st.pyplot(fig)

    # =====================================================
    # ERROR BAR
    # =====================================================

    elif prikaz == "error bar plot":

        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        fig.suptitle(
            "Стандардна девијација",
            fontsize=12,
            fontweight='bold',
            y=0.98
        )

        for i, p in enumerate(params):

            ax = axes.flatten()[i]

            stats = raw_df.groupby('Group')[p].agg(
                ['mean', 'std']
            )

            x_labels = [
                'Пацијенти',
                'Волонтери'
            ]

            x_pos = [1, 1.4]

            y = [
                stats.loc['Patients', 'mean'],
                stats.loc['Volunteers', 'mean']
            ]

            err = [
                stats.loc['Patients', 'std'],
                stats.loc['Volunteers', 'std']
            ]

            ax.errorbar(
                x_pos,
                y,
                yerr=err,
                fmt='o',
                color='black',
                ecolor='#e67e22',
                capsize=10,
                markersize=8
            )

            ax.set_xticks(x_pos)

            ax.set_xticklabels(x_labels)

            ax.set_xlim(0.5, 1.9)

            ax.set_title(
                p,
                fontweight='bold'
            )

            ax.grid(
                axis='y',
                linestyle='--',
                alpha=0.3
            )

        fig.tight_layout()

        st.pyplot(fig)

    # =====================================================
    # DOUGHNUT
    # =====================================================

    elif prikaz == "doughnut":

        fig, ax = plt.subplots(figsize=(8, 8))

        counts = raw_df['Group'].value_counts()

        ax.pie(
            [
                counts.get('Patients', 0),
                counts.get('Volunteers', 0)
            ],
            labels=['Пацијенти', 'Волонтери'],
            autopct='%1.1f%%',
            startangle=90,
            colors=['#ff7675', '#74b9ff'],
            wedgeprops={'width': 0.5}
        )

        ax.set_title(
            "Удио испитаника",
            fontweight='bold'
        )

        st.pyplot(fig)

    # =====================================================
    # RADAR CHART
    # =====================================================

    elif prikaz == "radar chart":

        fig = plt.figure(figsize=(8, 8))

        ax = fig.add_subplot(111, polar=True)

        for group, color, label in zip(
                ['Patients', 'Volunteers'],
                ['red', 'blue'],
                ['Пацијенти', 'Волонтери']):

            means = [
                raw_df[
                    raw_df['Group'] == group
                ][p].mean()
                for p in params
            ]

            norm_vals = [means[0]] + [
                v * 1000 for v in means[1:]
            ]

            norm_vals = np.append(
                norm_vals,
                norm_vals[0]
            )

            angles = np.linspace(
                0,
                2 * np.pi,
                len(params),
                endpoint=False
            ).tolist()

            angles += angles[:1]

            ax.fill(
                angles,
                norm_vals,
                color=color,
                alpha=0.1
            )

            ax.plot(
                angles,
                norm_vals,
                color=color,
                linewidth=2,
                label=label
            )

        ax.set_xticks(angles[:-1])

        ax.set_xticklabels(
            params,
            fontweight='bold'
        )

        ax.set_title(
            "Радарски приказ параметара",
            fontweight='bold',
            pad=20
        )

        ax.legend(
            loc='lower right',
            bbox_to_anchor=(1.2, 0)
        )

        st.pyplot(fig)

    # =====================================================
    # HISTOGRAM
    # =====================================================

    elif prikaz == "histogram":

        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        boja_pat = (0.90, 0.40, 0.20)

        boja_vol = (0.20, 0.40, 0.80)

        ranges = {
            'FA': (0.14, 0.185),
            'MD': (0.54, 0.76),
            'AD': (0.64, 0.86),
            'RD': (0.48, 0.70)
        }

        for i, p in enumerate(params):

            ax = axes.flatten()[i]

            p_data = raw_df[
                raw_df['Group'] == 'Patients'
            ][p].values

            v_data = raw_df[
                raw_df['Group'] == 'Volunteers'
            ][p].values

            if p != 'FA':

                p_data = p_data * 1000

                v_data = v_data * 1000

            start, end = ranges[p]

            zajednicki_bins = np.linspace(
                start,
                end,
                9
            )

            ax.hist(
                p_data,
                bins=zajednicki_bins,
                color=boja_pat,
                label='Пацијенти',
                edgecolor='white',
                alpha=0.6,
                linewidth=0.5
            )

            ax.hist(
                v_data,
                bins=zajednicki_bins,
                color=boja_vol,
                label='Волонтери',
                edgecolor='white',
                alpha=0.6,
                linewidth=0.5
            )

            ax.set_title(
                f"$\\mathit{{{p}}}$",
                fontsize=12
            )

            ax.set_ylabel(
                "Фреквенција",
                fontsize=10
            )

            jedinica = (
                " ($10^{-3}$ mm$^2$/s)"
                if p != 'FA'
                else ""
            )

            ax.set_xlabel(
                f"$\\mathit{{{p}}}${jedinica}",
                fontsize=10
            )

            ax.spines['top'].set_visible(False)

            ax.spines['right'].set_visible(False)

            ax.grid(
                True,
                linestyle='-',
                alpha=0.2
            )

        fig.tight_layout()

        fig.subplots_adjust(
            top=0.90,
            hspace=0.4
        )

        legend_elements = [
            Patch(
                facecolor=boja_pat,
                alpha=0.6,
                edgecolor='black',
                linewidth=0.5,
                label='Пацијенти'
            ),
            Patch(
                facecolor=boja_vol,
                alpha=0.6,
                edgecolor='black',
                linewidth=0.5,
                label='Волонтери'
            )
        ]

        fig.legend(
            handles=legend_elements,
            loc='upper center',
            ncol=2,
            bbox_to_anchor=(0.5, 1.0),
            frameon=True,
            edgecolor='black',
            fontsize=10
        )

        st.pyplot(fig)
