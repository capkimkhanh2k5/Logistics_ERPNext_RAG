-- ============================================================================
-- 002_apache_age_schema.sql
-- Cấu hình Apache AGE Graph Database Extension cho PostgreSQL
-- ============================================================================

-- 1. Kích hoạt extension Apache AGE nếu có trong môi trường PostgreSQL
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_available_extensions WHERE name = 'age'
    ) THEN
        EXECUTE 'CREATE EXTENSION IF NOT EXISTS age CASCADE;';
        RAISE NOTICE 'Apache AGE extension enabled successfully.';
    ELSE
        RAISE NOTICE 'Apache AGE extension is not installed on this PostgreSQL server. Fallback to relational/in-memory mode.';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Could not load Apache AGE extension: %', SQLERRM;
END $$;

-- 2. Tải AGE vào session và thiết lập search_path
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'age') THEN
        PERFORM load('age');
        SET search_path = ag_catalog, "$user", public;
        
        -- Khởi tạo đồ thị hải quan nếu chưa có
        IF NOT EXISTS (
            SELECT 1 FROM ag_catalog.ag_graph WHERE name = 'customs_tariff_graph'
        ) THEN
            PERFORM ag_catalog.create_graph('customs_tariff_graph');
            RAISE NOTICE 'Graph customs_tariff_graph created successfully.';
        END IF;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error initializing customs_tariff_graph: %', SQLERRM;
END $$;
