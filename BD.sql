CREATE DATABASE IF NOT EXISTS tienda_hardware_intelligence;
USE tienda_hardware_intelligence;

-- ====================================================================
-- BLOQUE 1: CATÁLOGO MAESTRO Y DATOS EXTERNOS (ETL / API)
-- ====================================================================

-- 1. Clasificación de rendimiento propia de la tienda
CREATE TABLE IF NOT EXISTS component_tiers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tier_name VARCHAR(50) NOT NULL UNIQUE, -- Ej: 'Gama Baja', 'Gama Media', 'Gama Alta'
    description TEXT
) ENGINE=InnoDB;

-- 2. Catálogo maestro de componentes (Ancla para homologar ETL y API)
CREATE TABLE IF NOT EXISTS components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE, -- Ej: 'GeForce RTX 3060'
    category VARCHAR(50) NOT NULL,    -- Ej: 'GPU', 'CPU', 'RAM', 'Storage'
    tier_id INT,
    FOREIGN KEY (tier_id) REFERENCES component_tiers(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 3. Precios de referencia del mercado externo (API - eBay)
CREATE TABLE IF NOT EXISTS market_prices_external (
    component_id INT PRIMARY KEY,
    price_clp INT NOT NULL, -- Usamos INT ya que el peso chileno no maneja centavos habitualmente
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Contexto del Mercado Global (ETL - Steam HW Survey)
CREATE TABLE IF NOT EXISTS steam_hardware_survey (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component_id INT NOT NULL,
    global_share_percentage DECIMAL(5,2) NOT NULL, -- Ej: 42.15
    survey_date DATE NOT NULL,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ====================================================================
-- BLOQUE 2: DEMANDA Y REQUISITOS (ETL - Kaggle)
-- ====================================================================

-- 5. Catálogo de videojuegos
CREATE TABLE IF NOT EXISTS games (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL UNIQUE,
    release_year INT
) ENGINE=InnoDB;

-- 6. Requisitos de hardware por juego
CREATE TABLE IF NOT EXISTS game_requirements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT NOT NULL,
    requirement_type ENUM('Minimum', 'Recommended') NOT NULL,
    component_id INT NOT NULL, -- Componente homologado que exige el juego
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
) ENGINE=InnoDB;


-- ====================================================================
-- BLOQUE 3: REALIDAD DE LA TIENDA Y SIMULACIÓN (MySQL Interno)
-- ====================================================================

-- 7. Inventario real de la tienda
CREATE TABLE IF NOT EXISTS store_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component_id INT NOT NULL UNIQUE,
    stock_qty INT NOT NULL DEFAULT 0,
    store_price_clp INT NOT NULL, -- Nuestro precio de venta actual
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 8. Historial de ventas de la tienda (Para calcular rotación/sobrestock)
CREATE TABLE IF NOT EXISTS store_sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    component_id INT NOT NULL,
    quantity_sold INT NOT NULL DEFAULT 1,
    sale_date DATE NOT NULL,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 9. Configuraciones de PC pre-armadas (Build Templates)
CREATE TABLE IF NOT EXISTS build_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_name VARCHAR(100) NOT NULL UNIQUE, -- Ej: 'Build Recomendada 1080p'
    description TEXT
) ENGINE=InnoDB;

-- 10. Tabla intermedia entre Builds y Componentes (Muchos a Muchos)
CREATE TABLE IF NOT EXISTS build_components (
    build_id INT NOT NULL,
    component_id INT NOT NULL,
    PRIMARY KEY (build_id, component_id),
    FOREIGN KEY (build_id) REFERENCES build_templates(id) ON DELETE CASCADE,
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 11. Consultas simuladas de usuarios
CREATE TABLE IF NOT EXISTS user_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    budget_clp INT NOT NULL, -- Ej: 500000
    target_game_id INT,      -- Juego que el usuario quiere correr
    query_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (target_game_id) REFERENCES games(id) ON DELETE SET NULL
) ENGINE=InnoDB;


-- ====================================================================
-- BLOQUE 4: ÍNDICES PARA OPTIMIZAR EL EDA (Análisis de Datos)
-- ====================================================================

CREATE INDEX idx_components_category ON components(category);
CREATE INDEX idx_inventory_stock ON store_inventory(stock_qty);
CREATE INDEX idx_sales_date ON store_sales(sale_date);
CREATE INDEX idx_requirements_type ON game_requirements(requirement_type);