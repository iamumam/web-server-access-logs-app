import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import io
import base64
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Web Server Access Logs Analysis",
    page_icon="📊",
    layout="wide"
)

# Title and introduction
st.title("📊 Web Server Access Logs Analysis")
st.markdown("""
### Kelompok 1 - Data Visualisasi A
**Anggota Kelompok:**
1. Dini Indriani (222410101040)
2. Anggun Mellanie (222410102029)
3. Lailatus Sya'diah (222410103009)
4. Mohammad Laily Nova Krisna (222410103048)
5. Mohammad Khotlibul Umam (222410103069)
6. Alifia Luthfi N. (222410103093)
""")

# Function to parse logs
def parse_logs(log_content):
    log_pattern = re.compile(
        r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s'                  # IP address
        r'- - \[(?P<datetime>[^\]]+)\]\s'                 # Timestamp
        r'"(?P<method>\w+)\s(?P<url>\S+)\sHTTP/\d\.\d"\s' # HTTP Method, URL
        r'(?P<status>\d{3})\s(?P<size>\d+|-)\s'           # Status code, Size
        r'"(?P<referrer>[^"]*)"\s'                        # Referrer
        r'"(?P<user_agent>[^"]*)"'                        # User Agent
    )
    
    log_data = []
    for line in log_content.split('\n'):
        if line.strip():  # Skip empty lines
            match = log_pattern.match(line)
            if match:
                entry = match.groupdict()
                entry['size'] = int(entry['size']) if entry['size'] != '-' else 0
                log_data.append(entry)
    
    # Create DataFrame
    df = pd.DataFrame(log_data)
    if not df.empty:
        df['status'] = df['status'].astype(int)
        df['datetime'] = pd.to_datetime(df['datetime'], format="%d/%b/%Y:%H:%M:%S %z")
        # Add hour column for time analysis
        df['hour'] = df['datetime'].dt.floor('H')
    
    return df

# Sidebar for file upload and options
st.sidebar.header("Upload and Options")

# File upload option
uploaded_file = st.sidebar.file_uploader("Upload Access Log File", type=["log", "txt"])

# Example data option
use_example_data = st.sidebar.checkbox("Use Example Data", value=True)

# Load data
df = None

if uploaded_file is not None:
    # Read uploaded file
    log_content = uploaded_file.getvalue().decode("utf-8")
    df = parse_logs(log_content)
    st.sidebar.success(f"Successfully loaded {len(df)} log entries")
elif use_example_data:
    # Generate some sample data based on patterns from the original file
    sample_logs = """
66.249.66.194 - - [12/Jan/2020:10:15:35 +0000] "GET /settings/logo HTTP/1.1" 200 3456 "https://example.com/dashboard" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
66.249.66.91 - - [12/Jan/2020:10:16:12 +0000] "GET /static/css/font/wyekan/font.woff HTTP/1.1" 200 1234 "https://example.com/products" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
207.46.13.9 - - [12/Jan/2020:10:17:05 +0000] "GET / HTTP/1.1" 200 7890 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
23.101.169.3 - - [12/Jan/2020:10:18:23 +0000] "GET /image/33888abcdef HTTP/1.1" 200 4567 "https://example.com/products/detail" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
207.46.13.136 - - [12/Jan/2020:10:19:45 +0000] "GET /image/11947xyz HTTP/1.1" 200 5678 "https://example.com/search" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
66.249.66.194 - - [12/Jan/2020:10:20:10 +0000] "GET /favicon.ico HTTP/1.1" 200 1122 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
91.99.72.15 - - [12/Jan/2020:10:21:30 +0000] "GET /image/goodShopping HTTP/1.1" 200 3344 "https://example.com" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X)"
40.77.167.170 - - [12/Jan/2020:10:22:15 +0000] "GET /image/bestPrice HTTP/1.1" 200 2233 "https://example.com/offers" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
5.237.18.117 - - [12/Jan/2020:10:23:05 +0000] "GET /image/warranty HTTP/1.1" 200 1987 "https://example.com/services" "Mozilla/5.0 (Linux; Android 9; SM-G950F)"
66.249.66.91 - - [12/Jan/2020:10:24:20 +0000] "GET /image/support HTTP/1.1" 200 2345 "https://example.com/contact" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
66.249.66.194 - - [12/Jan/2020:10:25:30 +0000] "GET /settings/logo HTTP/1.1" 200 3456 "https://example.com/dashboard" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
207.46.13.9 - - [12/Jan/2020:10:26:15 +0000] "GET /product/123 HTTP/1.1" 404 567 "https://example.com/search" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
66.249.66.91 - - [12/Jan/2020:10:27:40 +0000] "GET /static/js/main.js HTTP/1.1" 200 8976 "https://example.com" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
23.101.169.3 - - [12/Jan/2020:10:28:25 +0000] "GET /login HTTP/1.1" 302 0 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
207.46.13.136 - - [12/Jan/2020:10:29:10 +0000] "GET /about HTTP/1.1" 200 4532 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
66.249.66.194 - - [12/Jan/2020:10:30:05 +0000] "GET /contact HTTP/1.1" 200 3211 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
91.99.72.15 - - [12/Jan/2020:10:31:20 +0000] "GET /blog HTTP/1.1" 301 0 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X)"
40.77.167.170 - - [12/Jan/2020:10:32:45 +0000] "GET /blog/new HTTP/1.1" 200 6543 "https://example.com/blog" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
5.237.18.117 - - [12/Jan/2020:10:33:30 +0000] "GET /api/users HTTP/1.1" 403 321 "-" "Mozilla/5.0 (Linux; Android 9; SM-G950F)"
66.249.66.91 - - [12/Jan/2020:10:34:15 +0000] "GET /sitemap.xml HTTP/1.1" 200 5432 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
66.249.66.194 - - [12/Jan/2020:07:00:05 +0000] "GET /settings/logo HTTP/1.1" 200 3456 "https://example.com/dashboard" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
66.249.66.91 - - [12/Jan/2020:07:00:12 +0000] "GET /static/css/font/wyekan/font.woff HTTP/1.1" 200 1234 "https://example.com/products" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
207.46.13.9 - - [12/Jan/2020:07:00:05 +0000] "GET / HTTP/1.1" 200 7890 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
23.101.169.3 - - [12/Jan/2020:07:00:23 +0000] "GET /image/33888abcdef HTTP/1.1" 200 4567 "https://example.com/products/detail" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
207.46.13.136 - - [12/Jan/2020:07:00:45 +0000] "GET /image/11947xyz HTTP/1.1" 200 5678 "https://example.com/search" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
66.249.66.194 - - [12/Jan/2020:07:00:10 +0000] "GET /favicon.ico HTTP/1.1" 200 1122 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
91.99.72.15 - - [12/Jan/2020:07:00:30 +0000] "GET /image/goodShopping HTTP/1.1" 200 3344 "https://example.com" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X)"
207.46.13.9 - - [12/Jan/2020:08:00:05 +0000] "GET / HTTP/1.1" 200 7890 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
23.101.169.3 - - [12/Jan/2020:08:00:23 +0000] "GET /image/33888abcdef HTTP/1.1" 200 4567 "https://example.com/products/detail" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
207.46.13.136 - - [12/Jan/2020:08:00:45 +0000] "GET /image/11947xyz HTTP/1.1" 304 0 "https://example.com/search" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
66.249.66.194 - - [12/Jan/2020:14:15:35 +0000] "GET /settings/logo HTTP/1.1" 200 3456 "https://example.com/dashboard" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
66.249.66.91 - - [12/Jan/2020:14:16:12 +0000] "GET /static/css/font/wyekan/font.woff HTTP/1.1" 200 1234 "https://example.com/products" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
207.46.13.9 - - [12/Jan/2020:14:17:05 +0000] "GET / HTTP/1.1" 200 7890 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
23.101.169.3 - - [12/Jan/2020:14:18:23 +0000] "GET /image/33888abcdef HTTP/1.1" 304 0 "https://example.com/products/detail" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
207.46.13.136 - - [12/Jan/2020:14:19:45 +0000] "GET /image/11947xyz HTTP/1.1" 200 5678 "https://example.com/search" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
66.249.66.194 - - [12/Jan/2020:14:20:10 +0000] "GET /notfound HTTP/1.1" 404 1122 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
91.99.72.15 - - [12/Jan/2020:14:21:30 +0000] "GET /api/private HTTP/1.1" 403 344 "https://example.com" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X)"
40.77.167.170 - - [12/Jan/2020:14:22:15 +0000] "GET /image/bestPrice HTTP/1.1" 200 2233 "https://example.com/offers" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
5.237.18.117 - - [12/Jan/2020:14:23:05 +0000] "GET /server-error HTTP/1.1" 500 987 "https://example.com/services" "Mozilla/5.0 (Linux; Android 9; SM-G950F)"
66.249.66.91 - - [12/Jan/2020:14:24:20 +0000] "GET /image/support HTTP/1.1" 499 0 "https://example.com/contact" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
"""
    df = parse_logs(sample_logs)
    st.sidebar.info(f"Using example data with {len(df)} log entries")

# Proceed only if data is loaded
if df is not None and not df.empty:
    # Overview metrics
    st.header("📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Requests", f"{len(df):,}")
    with col2:
        st.metric("Unique IPs", f"{df['ip'].nunique():,}")
    with col3:
        success_rate = (df['status'] < 400).mean() * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    with col4:
        st.metric("Error Rate", f"{100 - success_rate:.1f}%")
    
    # Raw data preview with show/hide toggle
    with st.expander("👁️ Preview Raw Data"):
        st.dataframe(df.head(10))
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["Top URLs", "Top IPs", "HTTP Status Codes", "Requests Over Time"])
    
    with tab1:
        st.subheader("Top URLs Accessed")
        # Number selector for top N URLs
        top_n_urls = st.slider("Select number of top URLs to display", 5, 20, 10, key="urls_slider")
        
        # Calculate top URLs
        top_urls = df['url'].value_counts().head(top_n_urls)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        top_urls.plot(kind='barh', ax=ax, color='skyblue')
        ax.set_title(f'Top {top_n_urls} URLs Accessed')
        ax.set_xlabel('Number of Requests')
        ax.set_ylabel('URL')
        ax.invert_yaxis()  # To have the highest count at the top
        plt.tight_layout()
        
        # Display the plot
        st.pyplot(fig)
        
        # Explanation
        st.markdown("""
        ### Analysis:
        This visualization shows the most accessed URLs on the server. URLs with high request counts often represent:
        - Common resources loaded on multiple pages (CSS, fonts, logos)
        - Popular pages or endpoints
        - Resources requested by crawlers or bots
        
        A high number of requests to specific URLs may indicate areas where caching could be improved.
        """)
    
    with tab2:
        st.subheader("Top IP Addresses")
        # Number selector for top N IPs
        top_n_ips = st.slider("Select number of top IPs to display", 5, 20, 10, key="ips_slider")
        
        # Calculate top IPs
        top_ips = df['ip'].value_counts().head(top_n_ips)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        top_ips.plot(kind='barh', ax=ax, color='green')
        ax.set_title(f'Top {top_n_ips} IP Addresses by Number of Requests')
        ax.set_xlabel('Number of Requests')
        ax.set_ylabel('IP Address')
        ax.invert_yaxis()  # To have the highest count at the top
        plt.tight_layout()
        
        # Display the plot
        st.pyplot(fig)
        
        # Explanation
        st.markdown("""
        ### Analysis:
        This chart shows which IP addresses are making the most requests to the server:
        - IP addresses with very high request volumes often belong to bots, crawlers, or automated systems
        - Multiple high-volume IPs from the same subnet may indicate scraping activity
        - Unusual spikes from specific IPs might warrant investigation for security purposes
        
        IPs starting with 66.249.66.x are typically Google crawlers, while those starting with 207.46.13.x and 40.77.x.x often belong to Microsoft/Bing crawlers.
        """)
    
    with tab3:
        st.subheader("HTTP Status Code Distribution")
        
        # Calculate status code distribution
        status_counts = df['status'].value_counts().sort_index()
        
        # Create status code groups for coloring
        def status_color(code):
            if 200 <= code < 300:
                return 'success'
            elif 300 <= code < 400:
                return 'redirect'
            elif 400 <= code < 500:
                return 'client_error'
            else:
                return 'server_error'
        
        df['status_type'] = df['status'].apply(status_color)
        status_type_counts = df['status_type'].value_counts()
        
        # Create two columns for different views
        col1, col2 = st.columns(2)
        
        with col1:
            # Status code detailed view
            fig1, ax1 = plt.subplots(figsize=(8, 5))
            status_counts.plot(kind='bar', ax=ax1, color='orange')
            ax1.set_title('HTTP Status Code Distribution')
            ax1.set_xlabel('Status Code')
            ax1.set_ylabel('Count')
            ax1.tick_params(axis='x', rotation=0)
            plt.tight_layout()
            st.pyplot(fig1)
        
        with col2:
            # Status type view (grouped)
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            colors = {'success': 'green', 'redirect': 'blue', 'client_error': 'orange', 'server_error': 'red'}
            status_type_counts.plot(
                kind='pie', 
                ax=ax2,
                autopct='%1.1f%%',
                colors=[colors[s] for s in status_type_counts.index],
                explode=[0.05 if s != 'success' else 0 for s in status_type_counts.index]
            )
            ax2.set_title('HTTP Status Code Types')
            ax2.set_ylabel('')
            plt.tight_layout()
            st.pyplot(fig2)
        
        # Add a legend explaining status codes
        st.markdown("""
        ### HTTP Status Code Meanings:
        - **2xx (Success)**: Request was successfully received, understood, and accepted
          - 200: OK - Standard response for successful requests
        - **3xx (Redirection)**: Client must take additional action to complete the request
          - 301: Moved Permanently - URL has been permanently moved
          - 302: Found - Temporary redirect
          - 304: Not Modified - Resource has not been modified since last requested
        - **4xx (Client Error)**: Request contains bad syntax or cannot be fulfilled
          - 400: Bad Request - Server cannot understand the request
          - 403: Forbidden - Server refuses to authorize the request
          - 404: Not Found - Requested resource could not be found
          - 499: Client Closed Request - Client closed connection before server responded
        - **5xx (Server Error)**: Server failed to fulfill a valid request
          - 500: Internal Server Error - Generic server error message
          - 502: Bad Gateway - Server acting as gateway received invalid response
          - 504: Gateway Timeout - Server acting as gateway did not receive response in time
        """)
    
    with tab4:
        st.subheader("Requests Over Time")
        
        # Group by hour and count requests
        requests_per_hour = df.groupby('hour').size()
        
        # Create time plot
        fig, ax = plt.subplots(figsize=(12, 6))
        requests_per_hour.plot(kind='line', marker='o', color='purple', ax=ax)
        ax.set_title('Number of Requests Over Time')
        ax.set_xlabel('Time')
        ax.set_ylabel('Number of Requests')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Display the plot
        st.pyplot(fig)
        
        # Calculate peak hours
        peak_hour = requests_per_hour.idxmax()
        peak_requests = requests_per_hour.max()
        
        # Display peak information
        st.info(f"**Peak Traffic Hour:** {peak_hour.strftime('%Y-%m-%d %H:%M')} with {peak_requests:,} requests")
        
        # Explanation
        st.markdown("""
        ### Analysis:
        This time series visualization shows the number of requests to the server over time:
        - Peaks represent periods of high server load
        - The most significant peak occurs at 7:00 AM, which might represent:
          - Beginning of business hours when users start using the service
          - Scheduled jobs or backups running at that time
          - Automated crawling/indexing activity
        
        Understanding these patterns helps with:
        - Server capacity planning
        - Scheduling maintenance during low-traffic periods
        - Identifying abnormal traffic patterns that might indicate issues
        """)
    
    # Additional analysis section
    st.header("🔍 Additional Analysis")
    
    # User agent analysis (Browser vs Bot)
    def is_bot(user_agent):
        bot_patterns = ['bot', 'crawl', 'spider', 'slurp', 'bingbot', 'googlebot']
        return any(pattern in user_agent.lower() for pattern in bot_patterns)
    
    df['is_bot'] = df['user_agent'].apply(is_bot)
    bot_counts = df['is_bot'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Bot vs Human Traffic")
        fig, ax = plt.subplots(figsize=(8, 8))
        bot_counts.plot(
            kind='pie',
            labels=['Human', 'Bot'] if False in bot_counts.index else ['Bot'],
            autopct='%1.1f%%',
            colors=['lightblue', 'lightgreen'],
            explode=[0, 0.1] if False in bot_counts.index else [0],
            ax=ax
        )
        ax.set_title('Bot vs Human Traffic')
        ax.set_ylabel('')
        plt.tight_layout()
        st.pyplot(fig)
        
        # Bot explanation
        st.markdown("""
        ### Bot Traffic:
        A significant portion of web traffic often comes from bots rather than human users. These include:
        - Search engine crawlers (Google, Bing)
        - Monitoring tools
        - Security scanners
        - Feed fetchers
        
        High bot traffic is normal for public websites, but unusually high volumes may require investigation.
        """)
    
    with col2:
        st.subheader("Request Methods")
        method_counts = df['method'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 8))
        method_counts.plot(
            kind='pie',
            autopct='%1.1f%%',
            colors=sns.color_palette('pastel'),
            ax=ax
        )
        ax.set_title('HTTP Request Methods')
        ax.set_ylabel('')
        plt.tight_layout()
        st.pyplot(fig)
        
        # Method explanation
        st.markdown("""
        ### HTTP Methods:
        - **GET**: Retrieve data from the server (most common)
        - **POST**: Submit data to the server
        - **HEAD**: Same as GET but without response body
        - **PUT**: Upload a resource
        - **DELETE**: Remove a resource
        
        A high proportion of GET requests is typical for content websites, while APIs tend to have more variety in request methods.
        """)
    
    # Download processed data section
    st.header("💾 Export Data")
    
    # Function to convert dataframe to CSV for download
    def get_csv_download_link(df, filename="web_log_data.csv"):
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV File</a>'
        return href
    
    st.markdown(get_csv_download_link(df), unsafe_allow_html=True)
    
    # Footer with report generation time
    st.markdown("---")
    st.markdown(f"*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

else:
    # Show instructions if no data is loaded
    st.info("Please upload an access log file using the sidebar or use the example data to start.")
    
    st.markdown("""
    ### Expected Log Format
    
    This application expects web server access logs in the common format, for example:
    ```
    66.249.66.194 - - [12/Jan/2020:10:15:35 +0000] "GET /settings/logo HTTP/1.1" 200 3456 "https://example.com/dashboard" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    ```
    
    Where each line contains:
    - IP address
    - Identity, auth information (usually "-")
    - Timestamp in [day/month/year:hour:minute:second timezone] format
    - HTTP request method, URL, and protocol
    - Status code
    - Response size in bytes
    - Referrer URL
    - User agent string
    """)
