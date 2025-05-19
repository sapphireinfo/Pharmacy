import streamlit as st
import pandas as pd
import re
import plotly.express as px

st.set_page_config(page_title="Pharmacy Service Dashboard", layout="wide")
st.title("🏥 Pharmacy Service Performance Dashboard")

uploaded_file = st.file_uploader("📤 Upload PCC Excel File", type=["xlsx"])

if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file, sheet_name="Table 1", header=None)
        header_row_index = raw_df[raw_df.apply(lambda row: row.astype(str).str.contains("Jan-24").any(), axis=1)].index[0]
        
        true_header = raw_df.iloc[header_row_index]
        df = raw_df.iloc[header_row_index + 1:]
        df.columns = true_header
        df.reset_index(drop=True, inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        df.columns = df.columns.str.strip()
        df.fillna('', inplace=True)

        if 'JASMI LIMITED FRT03' in df.columns:
            df['JASMI LIMITED FRT03'] = df['JASMI LIMITED FRT03'].astype(str)
            df['JASMI LIMITED FRT03'] = df['JASMI LIMITED FRT03'].where(
                ~df['JASMI LIMITED FRT03'].duplicated(),
                df['JASMI LIMITED FRT03'] + '_' + df.groupby('JASMI LIMITED FRT03').cumcount().astype(str)
            )

        service_column = df.columns[0]

        # st.subheader("🔍 Data Preview")
        # st.dataframe(df)

        month_pattern = re.compile(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}$')
        months = [col for col in df.columns if isinstance(col, str) and month_pattern.match(col)]
        for month in months:
            df[month] = pd.to_numeric(df[month], errors='coerce')

        def show_line_chart(title, keyword, col):
            with col:
                st.markdown(f"### {title}")
                rows = df[df[service_column].astype(str).str.strip().str.upper() == keyword.upper()]
                if not rows.empty:
                    # Create base DataFrame with all months
                    chart_data = pd.DataFrame({'Month': months})
                    chart_data['Month_dt'] = pd.to_datetime(chart_data['Month'], format='%b-%y')

                    # Fetch values and merge
                    values = pd.to_numeric(rows.iloc[0][months], errors='coerce')
                    chart_data['Value'] = values.values

                    # Fill missing with 0 or NaN based on your choice
                    chart_data['Value'].fillna(0, inplace=True)  # Or use NaN if you want breaks instead of zero lines

                    # Sort properly
                    chart_data = chart_data.sort_values('Month_dt')

                    # Plot with consistent monthly ticks
                    fig = px.line(
                        chart_data,
                        x='Month_dt',
                        y='Value',
                        title=title,
                        markers=True,
                        labels={'Month_dt': 'Month', 'Value': title}
                    )

                    fig.update_layout(
                        xaxis_tickformat='%b %y',
                        xaxis=dict(
                            tickmode='linear',
                            dtick="M1"  # Force monthly ticks
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"⚠️ {title} service not found.")


        st.subheader("📊 Monthly Service Trends for Each Service – JASMI LIMITED (FRT03)")
        col1, col2 = st.columns(2)
        show_line_chart("NMS", "NMS", col1)
        show_line_chart("Blood Pressure", "BLOOD PRESSURE", col2)

        col3, col4 = st.columns(2)
        show_line_chart("P1 (NHS 111 & GP Referrals & Clin PW)", "P1 (NHS 111 & GP REFERRALS & CLIN PW)", col3)
        show_line_chart("Core Services (£)", "CORE SERVICES (£)", col4)

        col5, col6 = st.columns(2)
        show_line_chart("P1 Clinical Pathways", "P1 CLINICAL PATHWAYS", col5)
        show_line_chart("Covid Vac (Total for season)", "COVID VAC (TOTAL FOR SEASON)", col6)


#######Multi LIne CHart###########################################
        # JASMI LIMITED FRT03 services to plot
        multi_services = [
            "NMS",
            "BLOOD PRESSURE",
            "P1 (NHS 111 & GP REFERRALS & CLIN PW)",
            "P1 CLINICAL PATHWAYS",
            "COVID VAC (TOTAL FOR SEASON)",
            "Flu (TOTAL FOR SEASON)",
            "ABPM",
            "DMS",
            "OC",
            "LFD",
            "CPCS"
        ]

        # Prepare long-format DataFrame
        trend_rows = []
        for service in multi_services:
            row = df[df[service_column].astype(str).str.strip().str.upper() == service.upper()]
            if not row.empty:
                values = pd.to_numeric(row.iloc[0][months], errors='coerce')
                for month, value in zip(months, values):
                    # Use regex to remove any _ followed by digits
                    clean_label = re.sub(r'_\d+$', '', service).title()
                    trend_rows.append({
                        "Month": month,
                        "Service": clean_label,  # 👈 Used in legend and tooltip
                        "Value": value
                    })

        # Convert to DataFrame and format months
        trend_df = pd.DataFrame(trend_rows)
        trend_df["Month_dt"] = pd.to_datetime(trend_df["Month"], format="%b-%y")
        trend_df.sort_values(by="Month_dt", inplace=True)

        # Plot multi-line chart
        fig = px.line(
            trend_df,
            x="Month_dt",
            y="Value",
            color="Service",
            markers=True,
            title="📈 Monthly Trends of All Services: JASMI LIMITED FRT03)",
            labels={"Month_dt": "Month", "Value": "Count", "Service": "Service Type"},
            width=1000,
            height=600
        )

        fig.update_layout(
            xaxis_tickformat="%b %y",
            xaxis=dict(tickmode="linear", dtick="M1"),
            legend_title_text="Service",
            title_x=0.25,
            margin=dict(l=20, r=20, t=60, b=40)
        )

        st.plotly_chart(fig, use_container_width=False)

        # REVELSTOKE PHARMACY FE297 services to plot
        multi_services = [
            "NMS_1", 
            "BLOOD PRESSURE_1",
            "P1 (NHS 111 & GP REFERRALS & CLIN PW)_1",
            "P1 CLINICAL PATHWAYS_1",
            "COVID VAC (TOTAL FOR SEASON)_1",
            "Flu (TOTAL FOR SEASON)",
            "ABPM_1",
            "DMS_1",
            "OC_1",
            "LFD_1",
            "CPCS_1"
        ]

        # Prepare long-format DataFrame
        trend_rows = []
        for service in multi_services:
            row = df[df[service_column].astype(str).str.strip().str.upper() == service.upper()]
            if not row.empty:
                values = pd.to_numeric(row.iloc[0][months], errors='coerce')
                for month, value in zip(months, values):
                    # Use regex to remove any _ followed by digits
                    clean_label = re.sub(r'_\d+$', '', service).title()
                    trend_rows.append({
                        "Month": month,
                        "Service": clean_label,  # 👈 Used in legend and tooltip
                        "Value": value
                    })

        # Convert to DataFrame and format months
        trend_df_1 = pd.DataFrame(trend_rows)
        trend_df_1["Month_dt"] = pd.to_datetime(trend_df_1["Month"], format="%b-%y")
        trend_df_1.sort_values(by="Month_dt", inplace=True)

        # Plot multi-line chart for _1 services
        fig2 = px.line(
            trend_df_1,
            x="Month_dt",
            y="Value",
            color="Service",
            markers=True,
            title="📉 Monthly Trends of All Services: REVELSTOKE PHARMACY FE297",
            labels={"Month_dt": "Month", "Value": "Count", "Service": "Service Type"},
            width=1000,
            height=600
        )

        fig2.update_layout(
            xaxis_tickformat="%b %y",
            xaxis=dict(tickmode="linear", dtick="M1"),
            legend_title_text="Service",
            title_x=0.25,
            margin=dict(l=20, r=20, t=60, b=40)
        )

        st.plotly_chart(fig2, use_container_width=False)

        # TRINITY PHARMACY FKP10 services to plot
        multi_services = [
            "NMS_2", 
            "BLOOD PRESSURE_2",
            "P1 (NHS 111 & GP REFERRALS)",
            "P1 CLINICAL PATHWAYS_1",
            "COVID VAC (TOTAL FOR SEASON)_1",
            "Flu (TOTAL FOR SEASON)",
            "ABPM_2",
            "DMS_2",
            "OC_2",
            "LFD_2",
            "CPCS_2"
        ]

        # Prepare long-format DataFrame
        trend_rows = []
        for service in multi_services:
            row = df[df[service_column].astype(str).str.strip().str.upper() == service.upper()]
            if not row.empty:
                values = pd.to_numeric(row.iloc[0][months], errors='coerce')
                for month, value in zip(months, values):
                    clean_label = re.sub(r'_\d+$', '', service).title()
                    trend_rows.append({
                        "Month": month,
                        "Service": clean_label,  # 👈 Used in legend and tooltip
                        "Value": value
                    })

        # Convert to DataFrame and format months
        trend_df_1 = pd.DataFrame(trend_rows)
        trend_df_1["Month_dt"] = pd.to_datetime(trend_df_1["Month"], format="%b-%y")
        trend_df_1.sort_values(by="Month_dt", inplace=True)

        # Plot multi-line chart for _1 services
        fig2 = px.line(
            trend_df_1,
            x="Month_dt",
            y="Value",
            color="Service",
            markers=True,
            title="📉 Monthly Trends of All Services: TRINITY PHARMACY FKP10",
            labels={"Month_dt": "Month", "Value": "Count", "Service": "Service Type"},
            width=1000,
            height=600
        )

        fig2.update_layout(
            xaxis_tickformat="%b %y",
            xaxis=dict(tickmode="linear", dtick="M1"),
            legend_title_text="Service",
            title_x=0.25,
            margin=dict(l=20, r=20, t=60, b=40)
        )

        st.plotly_chart(fig2, use_container_width=False)

        # WOODBRIDGE PHARMACY FLD83 services to plot
        multi_services = [
            "NMS_3", 
            "BLOOD PRESSURE_3",
            "P1 (NHS 111 & GP REFERRALS)_1",
            "P1 CLINICAL PATHWAYS_3",
            "COVID VAC (TOTAL FOR SEASON)_3",
            "Flu (TOTAL FOR SEASON)",
            "ABPM_3",
            "DMS_3",
            "OC_3",
            "LFD_3",
            "CPCS_3"
        ]

        # Prepare long-format DataFrame
        trend_rows = []
        for service in multi_services:
            row = df[df[service_column].astype(str).str.strip().str.upper() == service.upper()]
            if not row.empty:
                values = pd.to_numeric(row.iloc[0][months], errors='coerce')
                for month, value in zip(months, values):
                    clean_label = re.sub(r'_\d+$', '', service).title()
                    trend_rows.append({
                        "Month": month,
                        "Service": clean_label,  # 👈 Used in legend and tooltip
                        "Value": value
                    })

        # Convert to DataFrame and format months
        trend_df_1 = pd.DataFrame(trend_rows)
        trend_df_1["Month_dt"] = pd.to_datetime(trend_df_1["Month"], format="%b-%y")
        trend_df_1.sort_values(by="Month_dt", inplace=True)

        # Plot multi-line chart for _1 services
        fig2 = px.line(
            trend_df_1,
            x="Month_dt",
            y="Value",
            color="Service",
            markers=True,
            title="📉 Monthly Trends of All Services: WOODBRIDGE PHARMACY FLD83",
            labels={"Month_dt": "Month", "Value": "Count", "Service": "Service Type"},
            width=1000,
            height=600
        )

        fig2.update_layout(
            xaxis_tickformat="%b %y",
            xaxis=dict(tickmode="linear", dtick="M1"),
            legend_title_text="Service",
            title_x=0.25,
            margin=dict(l=20, r=20, t=60, b=40)
        )

        st.plotly_chart(fig2, use_container_width=False)


#######BAR CHART###########################
        # PCM Comparison
        st.subheader("📊 P1 (NHS 111 & GP referrals & Clin PW) Services: Average PCM Comparison")

        # Mapping service keys to display names with pharmacy names
        target_services = {
            "P1 (NHS 111 & GP referrals & Clin PW)": "P1 (NHS 111 & GP referrals & Clin PW) (JASMI LIMITED FRT03)",
            "P1 (NHS 111 & GP referrals & Clin PW)_1": "P1 (NHS 111 & GP referrals & Clin PW) (REVELSTOKE PHARMACY FE297)",
            "P1 (NHS 111 & GP referrals)": "P1 (NHS 111 & GP referrals) (TRINITY PHARMACY FKP10)",
            "P1 (NHS 111 & GP referrals)_1": "P1 (NHS 111 & GP referrals) (WOODBRIDGE PHARMACY FLD83)"
        }

        # Define colors for each pharmacy display name
        color_map = {
            "P1 (NHS 111 & GP referrals & Clin PW) (JASMI LIMITED FRT03)": "red",
            "P1 (NHS 111 & GP referrals & Clin PW)_1 (REVELSTOKE PHARMACY FE297)": "orange",
            "P1 (NHS 111 & GP referrals) (TRINITY PHARMACY FKP10)": "blue",
            "P1 (NHS 111 & GP referrals)_1 (WOODBRIDGE PHARMACY FLD83)": "green"
        }

        pcm_data = {}
        for service_key, service_display in target_services.items():
            row = df[df[service_column].astype(str).str.strip().str.upper() == service_key.upper()]
            if not row.empty:
                try:
                    pcm_raw = row.iloc[0].get("Average PCM", "")
                    if pcm_raw != '':
                        pcm = round(float(pcm_raw))
                        pcm_data[service_display] = pcm
                except:
                    pass

        if pcm_data:
            chart_df = pd.DataFrame.from_dict(pcm_data, orient='index', columns=['Average PCM'])
            chart_df.reset_index(inplace=True)
            chart_df.rename(columns={'index': 'Service'}, inplace=True)

            # Display status messages
            for name, value in pcm_data.items():
                if value < 50:
                    st.markdown(
                        f"<div style='color:red; font-weight:bold;'>⚠️ {name}: Underperforming (PCM = {value})</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='color:green; font-weight:bold;'>✅ {name}: Performing Well (PCM = {value})</div>",
                        unsafe_allow_html=True
                    )

            # Plotly chart with legend and colors
            fig = px.bar(
                chart_df,
                x='Service',
                y='Average PCM',
                color='Service',
                text='Average PCM',
                color_discrete_map=color_map,  # 👈 assign fixed colors
                width=1000,
                height=700
            )

            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True  # 👈 keep legend
            )

            st.plotly_chart(fig, use_container_width=False)
        else:
            st.warning("⚠️ No valid Average PCM values found for selected P1 services.")


        st.subheader("📊 Blood Pressure Services: Average PCM Comparison")

        # Mapping service keys to display names with pharmacy names
        target_services = {
            "Blood Pressure": "Blood Pressure (JASMI LIMITED FRT03)",
            "Blood Pressure_1": "Blood Pressure (REVELSTOKE PHARMACY FE297)",
            "Blood Pressure_2": "Blood Pressure (TRINITY PHARMACY FKP10)",
            "Blood Pressure_3": "Blood Pressure (WOODBRIDGE PHARMACY FLD83)"
        }

        # Define colors for each pharmacy display name
        color_map = {
            "Blood Pressure (JASMI LIMITED FRT03)": "red",
            "Blood Pressure_1 (REVELSTOKE PHARMACY FE297)": "orange",
            "Blood Pressure_2 (TRINITY PHARMACY FKP10)": "blue",
            "Blood Pressure_3 (WOODBRIDGE PHARMACY FLD83)": "green"
        }

        pcm_data = {}
        for service_key, service_display in target_services.items():
            row = df[df[service_column].astype(str).str.strip().str.upper() == service_key.upper()]
            if not row.empty:
                try:
                    pcm_raw = row.iloc[0].get("Average PCM", "")
                    if pcm_raw != '':
                        pcm = round(float(pcm_raw))
                        pcm_data[service_display] = pcm
                except:
                    pass

        if pcm_data:
            chart_df = pd.DataFrame.from_dict(pcm_data, orient='index', columns=['Average PCM'])
            chart_df.reset_index(inplace=True)
            chart_df.rename(columns={'index': 'Service'}, inplace=True)

            # Display status messages
            for name, value in pcm_data.items():
                if value < 30:
                    st.markdown(
                        f"<div style='color:red; font-weight:bold;'>⚠️ {name}: Underperforming (PCM = {value})</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='color:green; font-weight:bold;'>✅ {name}: Performing Well (PCM = {value})</div>",
                        unsafe_allow_html=True
                    )

            # Plotly chart with legend and colors
            fig = px.bar(
                chart_df,
                x='Service',
                y='Average PCM',
                color='Service',
                text='Average PCM',
                color_discrete_map=color_map,  # 👈 assign fixed colors
                width=800,
                height=700
            )

            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True  # 👈 keep legend
            )

            st.plotly_chart(fig, use_container_width=False)
        else:
            st.warning("⚠️ No valid Average PCM values found for selected P1 services.")


        

        st.subheader("📊 DMS Services: Average PCM Comparison")

        # Mapping service keys to display names with pharmacy names
        target_services = {
            "DMS": "DMS (JASMI LIMITED FRT03)",
            "DMS_1": "DMS (REVELSTOKE PHARMACY FE297)",
            "DMS_2": "DMS (TRINITY PHARMACY FKP10)",
            "DMS_3": "DMS (WOODBRIDGE PHARMACY FLD83)"
        }

        # Define colors for each pharmacy display name
        color_map = {
            "DMS (JASMI LIMITED FRT03)": "red",
            "DMS_1 (REVELSTOKE PHARMACY FE297)": "orange",
            "DMS_2 (TRINITY PHARMACY FKP10)": "blue",
            "DMS_3 (WOODBRIDGE PHARMACY FLD83)": "green"
        }

        pcm_data = {}
        for service_key, service_display in target_services.items():
            row = df[df[service_column].astype(str).str.strip().str.upper() == service_key.upper()]
            if not row.empty:
                try:
                    pcm_raw = row.iloc[0].get("Average PCM", "")
                    if pcm_raw != '':
                        pcm = round(float(pcm_raw))
                        pcm_data[service_display] = pcm
                except:
                    pass

        if pcm_data:
            chart_df = pd.DataFrame.from_dict(pcm_data, orient='index', columns=['Average PCM'])
            chart_df.reset_index(inplace=True)
            chart_df.rename(columns={'index': 'Service'}, inplace=True)

            # Display status messages
            for name, value in pcm_data.items():
                if value < 20:
                    st.markdown(
                        f"<div style='color:red; font-weight:bold;'>⚠️ {name}: Underperforming (PCM = {value})</div>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<div style='color:green; font-weight:bold;'>✅ {name}: Performing Well (PCM = {value})</div>",
                        unsafe_allow_html=True
                    )

            # Plotly chart with legend and colors
            fig = px.bar(
                chart_df,
                x='Service',
                y='Average PCM',
                color='Service',
                text='Average PCM',
                color_discrete_map=color_map,  # 👈 assign fixed colors
                width=800,
                height=700
            )

            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=True  # 👈 keep legend
            )

            st.plotly_chart(fig, use_container_width=False)
        else:
            st.warning("⚠️ No valid Average PCM values found for selected P1 services.")


    except Exception as e:
        st.error(f"❌ An error occurred: {e}")
else:
    st.info("👈 Please upload a file to begin analysis.")
