# xosproject/xos-gui-extension-rcord-base
FROM xosproject/xos-gui-builder:1.0.0 as xos-rcord-base

ENV CODE_SOURCE .
ENV CODE_DEST /var/www
ENV VHOST /var/www/dist

COPY ${CODE_SOURCE}/package.json ${CODE_DEST}/package.json
COPY ${CODE_SOURCE}/typings.json ${CODE_DEST}/typings.json

WORKDIR ${CODE_DEST}
RUN npm install
RUN npm run typings

COPY ${CODE_SOURCE}/conf ${CODE_DEST}/conf
COPY ${CODE_SOURCE}/gulp_tasks ${CODE_DEST}/gulp_tasks
COPY ${CODE_SOURCE}/src ${CODE_DEST}/src
COPY ${CODE_SOURCE}/gulpfile.js ${CODE_DEST}/gulpfile.js
COPY ${CODE_SOURCE}/tsconfig.json ${CODE_DEST}/tsconfig.json
COPY ${CODE_SOURCE}/tslint.json ${CODE_DEST}/tslint.json
RUN npm run build

# xosproject/gui-extension-rcord
FROM alpine:3.7

ENV VHOST /var/www/dist
WORKDIR ${VHOST}

COPY --from=xos-rcord-base ${VHOST} /tmp

ARG org_label_schema_schema_version=1.0
ARG org_label_schema_name=xos-gui-extension-rcord
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown
ARG org_opencord_component_xos_gui_version=unknown
ARG org_opencord_component_xos_gui_vcs_url=unknown
ARG org_opencord_component_xos_gui_vcs_ref=unknown

LABEL org.label-schema.schema-version=$org_label_schema_schema_version \
      org.label-schema.name=$org_label_schema_name \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date \
      org.opencord.component.xos-gui.version=$org_opencord_component_xos_gui_version \
      org.opencord.component.xos-gui.vcs-url=$org_opencord_component_xos_gui_vcs_url \
      org.opencord.component.xos-gui.vcs-ref=$org_opencord_component_xos_gui_vcs_ref
