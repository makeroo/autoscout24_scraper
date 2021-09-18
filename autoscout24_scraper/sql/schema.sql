CREATE TABLE maker_model (
    model VARCHAR(200) NOT NULL,
    version VARCHAR(255),
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
    other TEXT -- json
)