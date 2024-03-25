FROM python:3.9-slim

WORKDIR /code

COPY . .

# Create directory and copy config.toml
RUN mkdir -p ~/.streamlit && cp config.toml ~/.streamlit/config.toml

# Set Streamlit configurations as environment variables
ENV STREAMLIT_GLOBAL_DEVELOPMENTMODE=false
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHERUSAGESTATS=false

RUN apt-get update && apt-get install -y curl
ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
RUN /install.sh && rm /install.sh

RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health