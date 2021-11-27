CREATE TABLE maker_model (
    id INTEGER,
    model VARCHAR(200) NOT NULL,
    version VARCHAR(255) NOT NULL,

    UNIQUE(model, version),
    PRIMARY KEY(id)
);

CREATE TABLE ad(
    id INTEGER,
    model_id INTEGER NOT NULL,
    ad_id VARCHAR NOT NULL,

    UNIQUE(ad_id),
    FOREIGN KEY (model_id) REFERENCES maker_model(id) ON DELETE CASCADE,
    PRIMARY KEY(id)
);

CREATE TABLE ad_update (
    id INTEGER,
    ad_id INTEGER NOT NULL,

    first_fetch INTEGER NOT NULL,
    last_fetch INTEGER NOT NULL,

    description TEXT,
    price DECIMAL(10,2),
    purchase_details TEXT, -- json
    mileage VARCHAR(100),
    first_registration VARCHAR(30),
    offer_type VARCHAR(30),
    previous_owners VARCHAR(60),
    transmission_type VARCHAR(60),
    combined_consumption VARCHAR(255),
    co2_emission VARCHAR(255),
    unknown_details TEXT, -- json
    other TEXT, -- json

    PRIMARY KEY(id)
);

