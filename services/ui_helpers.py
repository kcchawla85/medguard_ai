import streamlit as st


def inject_custom_css():
    st.markdown(
        """
        <style>
        .info-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 16px;
            border-radius: 14px;
            margin-bottom: 12px;
        }
        .field-label {
            font-size: 0.85rem;
            color: #9aa4b2;
            margin-bottom: 2px;
        }
        .field-value {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 700;
            margin-right: 8px;
        }
        .badge-low {
            background: rgba(34,197,94,0.15);
            color: #4ade80;
        }
        .badge-medium {
            background: rgba(245,158,11,0.15);
            color: #fbbf24;
        }
        .badge-high {
            background: rgba(239,68,68,0.15);
            color: #f87171;
        }
        .badge-pending {
            background: rgba(59,130,246,0.15);
            color: #60a5fa;
        }
        .badge-approved {
            background: rgba(34,197,94,0.15);
            color: #4ade80;
        }
        .badge-rejected {
            background: rgba(239,68,68,0.15);
            color: #f87171;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_field(label: str, value):
    st.markdown(f"<div class='field-label'>{label}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='field-value'>{value}</div>", unsafe_allow_html=True)


def render_badge(text: str, kind: str):
    st.markdown(
        f"<span class='badge badge-{kind}'>{text}</span>",
        unsafe_allow_html=True
    )