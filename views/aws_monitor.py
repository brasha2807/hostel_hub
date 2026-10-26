import streamlit as st
import os
import time as pytime
from config.aws_config import AWS_REGION, AWS_S3_BUCKET
from utils import aws_utils
from config.settings import STATIC_DIR, DB_PATH


def render_aws_monitor():
    st.title("☁️ AWS Cloud & Infrastructure Hub")
    st.caption("Live monitoring of Amazon Web Services (AWS) connectivity, S3 cloud storage buckets, EC2 virtual servers, and automated database backups.")

    # 1. AWS Connection Verification
    aws_status = aws_utils.check_aws_connection()

    if aws_status["connected"]:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 78, 59, 0.25) 100%);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 20px;
            padding: 24px 28px;
            margin-bottom: 24px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.3);
        ">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="font-size: 38px;">🟢</span>
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #34D399; font-weight: 800;">
                            AWS Cloud Infrastructure Active
                        </div>
                        <h2 style="margin: 2px 0 0 0; color: #FFFFFF !important; font-size: 24px; font-weight: 850;">
                            Connected to AWS Account #{aws_status['account_id']}
                        </h2>
                    </div>
                </div>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span class="pill-badge pill-success">Region: {aws_status['region']}</span>
                    <span class="pill-badge pill-info">IAM: Root / Admin</span>
                    <span class="pill-badge pill-warning">Boto3 v1.43 Ready</span>
                </div>
            </div>
            <div style="margin-top: 14px; font-size: 13px; color: #CBD5E1; font-family: monospace;">
                <strong>Identity ARN:</strong> {aws_status['arn']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(153, 27, 27, 0.25) 100%);
            border: 1px solid rgba(239, 68, 68, 0.4);
            border-radius: 20px;
            padding: 24px 28px;
            margin-bottom: 24px;
        ">
            <div style="display: flex; align-items: center; gap: 14px;">
                <span style="font-size: 38px;">⚠️</span>
                <div>
                    <h3 style="margin: 0; color: #F87171 !important;">AWS Disconnected or Missing Credentials</h3>
                    <p style="margin: 4px 0 0 0; color: #FCA5A5; font-size: 13px;">
                        {aws_status['error']}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3 Section Tabs
    tab_s3, tab_ec2, tab_backup = st.tabs([
        "🪣 Amazon S3 Cloud Storage",
        "🖥️ Amazon EC2 Instance Telemetry",
        "💾 Database Cloud Backups"
    ])

    # =========================================================
    # TAB 1: AMAZON S3 STORAGE
    # =========================================================
    with tab_s3:
        st.subheader("Amazon Simple Storage Service (S3)")
        st.caption("Hostel Hub uses S3 to persist high-resolution student portraits, facility tour videos, and administrative media assets.")

        bucket_info = aws_utils.check_bucket_status()

        c_s1, c_s2 = st.columns([2, 1])
        with c_s1:
            with st.container(border=True):
                st.markdown(f"**Target S3 Bucket:** `{bucket_info['bucket_name']}`")
                st.markdown(f"**AWS Region:** `{AWS_REGION}`")
                if bucket_info["exists"]:
                    st.success(f"Bucket exists and is accessible. Total indexed objects: {bucket_info.get('object_count', 0)}")
                else:
                    st.warning(f"Status: {bucket_info['error']}")

        with c_s2:
            with st.container(border=True):
                st.markdown("#### S3 Actions")
                if not bucket_info["exists"]:
                    if st.button("🚀 Create S3 Storage Bucket", type="primary", use_container_width=True):
                        ok, msg = aws_utils.create_s3_storage_bucket()
                        if ok:
                            st.success(msg)
                            pytime.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Failed to create bucket: {msg}")
                else:
                    st.markdown("<span style='color:#34D399; font-weight:700;'>✔ S3 Bucket Online</span>", unsafe_allow_html=True)

        # Media Sync Utility
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### 🔄 Sync Local Media Assets to AWS S3")
            st.caption("Upload local avatars, student photos, banners, and video files to Amazon S3.")

            if st.button("Sync All Static Media to S3", use_container_width=True):
                if not bucket_info["exists"]:
                    st.error("Please create the S3 bucket first above.")
                else:
                    with st.spinner("Syncing media files to AWS S3..."):
                        uploaded_count = 0
                        for root, _, files in os.walk(STATIC_DIR):
                            for file in files:
                                full_file = os.path.join(root, file)
                                rel_key = os.path.relpath(full_file, STATIC_DIR).replace("\\", "/")
                                s3_key = f"static/{rel_key}"
                                ok, _ = aws_utils.upload_file_to_s3(full_file, s3_key)
                                if ok:
                                    uploaded_count += 1
                        st.success(f"🎉 Successfully uploaded {uploaded_count} media files to Amazon S3 bucket `{bucket_info['bucket_name']}`!")

    # =========================================================
    # TAB 2: AMAZON EC2 TELEMETRY
    # =========================================================
    with tab_ec2:
        st.subheader("Amazon Elastic Compute Cloud (EC2)")
        st.caption("Inspect virtual compute instances in your configured AWS region and access automated deployment configurations.")

        instances = aws_utils.get_ec2_instances_summary()

        if instances:
            st.markdown(f"**Found {len(instances)} EC2 Instance(s) in `{AWS_REGION}`:**")
            st.dataframe(instances, use_container_width=True, hide_index=True)
        else:
            st.info(f"No active EC2 instances currently found in region `{AWS_REGION}`.")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("#### 🚀 Ready-to-Deploy EC2 Artifacts")
            st.write("This project includes enterprise-grade deployment configurations inside the `deploy/` directory:")
            st.markdown("""
            - **`deploy/Dockerfile`**: Hardened Python 3.13 production container with health checks.
            - **`deploy/docker-compose.yml`**: One-command service orchestration with volume persistence.
            - **`deploy/nginx.conf`**: High-performance reverse proxy with WebSocket stream support & SSL readiness.
            - **`deploy/hostelhub.service`**: Linux systemd unit file for auto-restart on boot.
            - **`deploy/setup_ec2.sh`**: Single-line automated bootstrap script for Amazon Linux 2023 or Ubuntu EC2.
            """)

            st.code("bash deploy/setup_ec2.sh", language="bash")

    # =========================================================
    # TAB 3: DATABASE CLOUD BACKUPS
    # =========================================================
    with tab_backup:
        st.subheader("Amazon S3 Disaster Recovery & Database Backup")
        st.caption("Perform on-demand snapshots of the SQLite database (`hostel_hub.db`) and store them in secure S3 storage.")

        c_bk1, c_bk2 = st.columns([2, 1])
        with c_bk1:
            with st.container(border=True):
                st.markdown(f"**Database File:** `{DB_PATH}`")
                if os.path.exists(DB_PATH):
                    sz = os.path.getsize(DB_PATH) / 1024
                    st.markdown(f"**Database File Size:** `{sz:.1f} KB`")
                    st.markdown("**Backup Target:** `s3://hostelhub-media-474333173964/backups/`")
                else:
                    st.error("Database file not found.")

        with c_bk2:
            st.write("")
            st.write("")
            if st.button("💾 Backup Database to S3 Now", type="primary", use_container_width=True):
                with st.spinner("Uploading database snapshot to S3..."):
                    ok, res = aws_utils.backup_database_to_s3()
                    if ok:
                        st.success(f"✅ {res}")
                    else:
                        st.error(f"Backup failed: {res}")
