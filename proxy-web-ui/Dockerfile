FROM node:18

# RUN useradd -ms /bin/sh -u 1001 app
# USER app

# Install dependencies
WORKDIR /app
COPY package.json ./

RUN npm install -g npm
RUN npm install -g pnpm
RUN pnpm install


COPY --chown=app:app . /app