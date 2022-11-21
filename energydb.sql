CREATE TABLE energydb(
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sensor TEXT NOT NULL,
    value VARCHAR(50) NOT NULL,
    PRIMARY KEY(created_at,value))
    PARTITION BY RANGE (created_at);

CREATE TABLE acc_energydb(
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sensor TEXT NOT NULL,
    value VARCHAR(50) NOT NULL,
    PRIMARY KEY(created_at,value))
    PARTITION BY RANGE (created_at);