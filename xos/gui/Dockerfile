FROM xosproject/xos-gui-extension-builder:candidate

# Set environment vars
ENV CODE_SOURCE .
ENV CODE_DEST /var/www
ENV VHOST /var/www/dist

# Add the app deps
COPY ${CODE_SOURCE}/package.json ${CODE_DEST}/package.json
COPY ${CODE_SOURCE}/typings.json ${CODE_DEST}/typings.json

# Install Deps
WORKDIR ${CODE_DEST}
RUN npm install
RUN npm run typings

# Build the app
COPY ${CODE_SOURCE}/conf ${CODE_DEST}/conf
COPY ${CODE_SOURCE}/gulp_tasks ${CODE_DEST}/gulp_tasks
COPY ${CODE_SOURCE}/src ${CODE_DEST}/src
COPY ${CODE_SOURCE}/gulpfile.js ${CODE_DEST}/gulpfile.js
COPY ${CODE_SOURCE}/tsconfig.json ${CODE_DEST}/tsconfig.json
COPY ${CODE_SOURCE}/tslint.json ${CODE_DEST}/tslint.json
RUN npm run build
