
-- ===============================
-- ELIMINAR TABLAS EN ORDEN CORRECTO
-- ===============================

DROP TABLE IF EXISTS app_general_properties;
DROP TABLE IF EXISTS microservice_properties_directory;
DROP TABLE IF EXISTS datastage_properties_directory;
DROP TABLE IF EXISTS database_properties_directory;
DROP TABLE IF EXISTS was_properties_directory;
DROP TABLE IF EXISTS pims_properties_directory;
DROP TABLE IF EXISTS app_directory;
DROP TABLE IF EXISTS appname_directory;
DROP TABLE IF EXISTS project_directory;
DROP TABLE IF EXISTS env_directory;
DROP TABLE IF EXISTS country_directory;
DROP TABLE IF EXISTS label_directory;
DROP TABLE IF EXISTS app_type_directory;
DROP TABLE IF EXISTS pipeline_properties_directory;
DROP TABLE IF EXISTS runtime_directory;
DROP TABLE IF EXISTS person_in_charge;
DROP TABLE IF EXISTS security_champion;
DROP TABLE IF EXISTS usage_directory;
DROP TABLE IF EXISTS token_directory;
DROP TABLE IF EXISTS openshift_properties_directory;
DROP TABLE IF EXISTS path_directory;
DROP TABLE IF EXISTS image_directory;


-- ===============================
-- CREACIÓN DE TABLAS
-- ===============================

CREATE TABLE project_directory (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(100) NOT NULL,
    project_acronym VARCHAR(100) NOT NULL
);

CREATE TABLE appname_directory (
    id SERIAL PRIMARY KEY,
    app TEXT NOT NULL
);

CREATE TABLE app_directory (
    id SERIAL PRIMARY KEY,
    id_appname INT REFERENCES appname_directory(id),
    repo_name TEXT NOT NULL,
    repo_url TEXT NOT NULL
);

CREATE TABLE env_directory (
    id SERIAL PRIMARY KEY,
    env VARCHAR(100) NOT NULL
);

CREATE TABLE country_directory (
    id SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE label_directory (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL
);

CREATE TABLE app_type_directory (
    id SERIAL PRIMARY KEY,
    app_type VARCHAR(100) NOT NULL
);

CREATE TABLE pipeline_properties_directory (
    id SERIAL PRIMARY KEY,
    securitygate BOOLEAN DEFAULT TRUE,
    unittests BOOLEAN DEFAULT TRUE,
    sonarqube BOOLEAN DEFAULT TRUE,
    qualitygate BOOLEAN DEFAULT TRUE
);

CREATE TABLE runtime_directory (
    id SERIAL PRIMARY KEY,
    runtime_name VARCHAR(100) NOT NULL,
    version_path VARCHAR(100) NOT NULL
);

CREATE TABLE person_in_charge (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE security_champion (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100)
);

CREATE TABLE token_directory (
    id SERIAL PRIMARY KEY,
    token TEXT,
    namespace_name VARCHAR(100)
);

CREATE TABLE openshift_properties_directory (
    id SERIAL PRIMARY KEY,
    secrets_enabled BOOLEAN DEFAULT TRUE,
    configmap_enabled BOOLEAN DEFAULT TRUE,
    volume_enabled BOOLEAN DEFAULT TRUE
);

CREATE TABLE usage_directory (
    id SERIAL PRIMARY KEY,
    usage VARCHAR(100)
);

CREATE TABLE image_directory (
    id SERIAL PRIMARY KEY,
    image_name VARCHAR(100)
);

CREATE TABLE path_directory (
    id SERIAL PRIMARY KEY,
    volume_path VARCHAR(100)
);

CREATE TABLE microservice_properties_directory (
    id SERIAL PRIMARY KEY,
    id_usage_directory INT REFERENCES usage_directory(id),
    cpulimits VARCHAR(100),
    cpurequest VARCHAR(100),
    memorylimits VARCHAR(100),
    memoryrequest VARCHAR(100),
    replicas INT,
    id_token_directory INT REFERENCES token_directory(id),
    id_openshift_properties_directory INT REFERENCES openshift_properties_directory(id),
    id_path_directory INT REFERENCES path_directory(id),
    drs_enabled BOOLEAN DEFAULT FALSE,
    id_image_directory INT REFERENCES image_directory(id)
);

CREATE TABLE datastage_properties_directory (
    id SERIAL PRIMARY KEY
);

CREATE TABLE database_properties_directory (
    id SERIAL PRIMARY KEY
);

CREATE TABLE was_properties_directory (
    id SERIAL PRIMARY KEY,
    host VARCHAR(100),
    instance_name VARCHAR(100),
    context_root VARCHAR(100)
);

CREATE TABLE pims_properties_directory (
    id SERIAL PRIMARY KEY,
    nexus_url VARCHAR(100)
);

CREATE TABLE app_general_properties (
    id SERIAL PRIMARY KEY,
    id_project_directory INT REFERENCES project_directory(id),
    id_app_directory INT REFERENCES app_directory(id),
    id_person_in_charge INT REFERENCES person_in_charge(id),
    id_security_champion INT REFERENCES security_champion(id),
    id_env_directory INT REFERENCES env_directory(id),
    id_country_directory INT REFERENCES country_directory(id),
    id_label_directory INT REFERENCES label_directory(id),
    id_app_type_directory INT REFERENCES app_type_directory(id),
    id_pipeline_properties_directory INT REFERENCES pipeline_properties_directory(id),
    id_runtime_directory INT REFERENCES runtime_directory(id),
    sonarqubepath_exec VARCHAR(100),
    id_microservice_directory INT REFERENCES microservice_properties_directory(id),
    id_datastage_properties_directory INT REFERENCES datastage_properties_directory(id),
    id_database_properties_directory INT REFERENCES database_properties_directory(id),
    id_was_properties_directory INT REFERENCES was_properties_directory(id),
    id_pims_properties_directory INT REFERENCES pims_properties_directory(id)
);
