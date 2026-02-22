# # pull official base image
FROM python:3.14-slim AS python-base

# Define application directory and user
ENV APP_HOME=/home/python_user
ENV APP_USER=python_user

RUN adduser --disabled-password --gecos "" $APP_USER
RUN chown -R $APP_USER:$APP_USER $APP_HOME

WORKDIR $APP_HOME

# Set timezone and install tzdata
ENV TZ='Asia/Tehran'
RUN echo $TZ > /etc/timezone && apt-get update && \
    apt-get install -y --no-install-recommends tzdata curl make && \
    rm -f /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables to optimize Python runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=$APP_HOME

# Upgrade pip
RUN pip install --upgrade pip

# Switch to non-root user for added security
# USER $APP_USER

# ------------------------------------------------------------------
# Stage: Set Up Environment
# ------------------------------------------------------------------
FROM python-base AS move-watchlist-app-base

COPY --chown=$APP_USER:$APP_USER Makefile $APP_HOME/Makefile

RUN make setup

COPY --chown=$APP_USER:$APP_USER pyproject.toml README.md $APP_HOME/
COPY --chown=$APP_USER:$APP_USER LICENSE $APP_HOME/LICENSE

RUN make install

ENV PATH="/root/.local/bin:$PATH"

# ------------------------------------------------------------------
# Stage: Final Application Image
# ------------------------------------------------------------------
FROM move-watchlist-app-base AS move-watchlist-app-final

COPY --chown=$APP_USER:$APP_USER scripts/ $APP_HOME/scripts/
COPY --chown=$APP_USER:$APP_USER src/ $APP_HOME/src/
COPY --chown=$APP_USER:$APP_USER migrations $APP_HOME/migrations
COPY --chown=$APP_USER:$APP_USER alembic.ini $APP_HOME/alembic.ini
COPY --chown=$APP_USER:$APP_USER manage.py $APP_HOME/manage.py

RUN chmod +x $APP_HOME/scripts/*

# USER $APP_USER

# EXPOSE 3000

# HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
#     CMD curl -f http://localhost:3000/api/v1/health || exit 1

# CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000", "--workers", "2", "--log-level", "info"]
