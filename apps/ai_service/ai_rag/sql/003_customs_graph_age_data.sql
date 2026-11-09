-- Apache AGE Data Migration for Customs Tariff Graph
LOAD 'age';
SET search_path = ag_catalog, '$user', public;

SELECT * FROM cypher('customs_tariff_graph', $$ CREATE (:TariffRoot {id: 'ROOT_CUSTOMS_TARIFF', name: 'Biểu Thuế XNK Việt Nam'}) $$) as (v agtype);
SELECT * FROM cypher('customs_tariff_graph', $$ CREATE (:Section {id: 'SXVI-S-XVI', label: 'Phần XVI', section: 'XVI', chapter: 'None'}) $$) as (v agtype);
SELECT * FROM cypher('customs_tariff_graph', $$ CREATE (:Chapter {id: 'SXVI-CH-84', label: 'Chương 84', section: 'XVI', chapter: '84'}) $$) as (v agtype);
SELECT * FROM cypher('customs_tariff_graph', $$ CREATE (:Chapter {id: 'SXVI-CH-85', label: 'Chương 85', section: 'XVI', chapter: '85'}) $$) as (v agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-S-XVI'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-S-XVI'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8401'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8401'}), (b {id: 'SXVI-T-84011000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8401'}), (b {id: 'SXVI-T-84012000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8401'}), (b {id: 'SXVI-T-84013000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8401'}), (b {id: 'SXVI-T-84014000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8402'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8402'}), (b {id: 'SXVI-T-840211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840211'}), (b {id: 'SXVI-T-84021110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840211'}), (b {id: 'SXVI-T-84021120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8402'}), (b {id: 'SXVI-T-840212'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840212'}), (b {id: 'SXVI-T-84021211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840212'}), (b {id: 'SXVI-T-84021219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840212'}), (b {id: 'SXVI-T-84021221'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840212'}), (b {id: 'SXVI-T-84021229'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8402'}), (b {id: 'SXVI-T-840219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840219'}), (b {id: 'SXVI-T-84021911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840219'}), (b {id: 'SXVI-T-84021919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840219'}), (b {id: 'SXVI-T-84021921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840219'}), (b {id: 'SXVI-T-84021929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8402'}), (b {id: 'SXVI-T-840220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840220'}), (b {id: 'SXVI-T-84022010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840220'}), (b {id: 'SXVI-T-84022020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8402'}), (b {id: 'SXVI-T-840290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840290'}), (b {id: 'SXVI-T-84029010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840290'}), (b {id: 'SXVI-T-84029090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8403'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8403'}), (b {id: 'SXVI-T-84031000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8403'}), (b {id: 'SXVI-T-840390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840390'}), (b {id: 'SXVI-T-84039010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840390'}), (b {id: 'SXVI-T-84039090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8404'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8404'}), (b {id: 'SXVI-T-840410'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840410'}), (b {id: 'SXVI-T-84041011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840410'}), (b {id: 'SXVI-T-84041019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840410'}), (b {id: 'SXVI-T-84041020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8404'}), (b {id: 'SXVI-T-84042000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8404'}), (b {id: 'SXVI-T-840490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840490'}), (b {id: 'SXVI-T-84049011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840490'}), (b {id: 'SXVI-T-84049019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840490'}), (b {id: 'SXVI-T-84049021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840490'}), (b {id: 'SXVI-T-84049029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840490'}), (b {id: 'SXVI-T-84049090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8405'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8405'}), (b {id: 'SXVI-T-84051000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8405'}), (b {id: 'SXVI-T-84059000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8406'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8406'}), (b {id: 'SXVI-T-84061000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8406'}), (b {id: 'SXVI-T-84068100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8406'}), (b {id: 'SXVI-T-840682'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840682'}), (b {id: 'SXVI-T-84068210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840682'}), (b {id: 'SXVI-T-84068290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8406'}), (b {id: 'SXVI-T-84069000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-84071000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-840721'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840721'}), (b {id: 'SXVI-T-84072110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840721'}), (b {id: 'SXVI-T-84072190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-840729'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840729'}), (b {id: 'SXVI-T-84072920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840729'}), (b {id: 'SXVI-T-84072990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-84073100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-840732'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840732'}), (b {id: 'SXVI-T-84073211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840732'}), (b {id: 'SXVI-T-84073212'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840732'}), (b {id: 'SXVI-T-84073219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840732'}), (b {id: 'SXVI-T-84073222'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840732'}), (b {id: 'SXVI-T-84073229'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-840733'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840733'}), (b {id: 'SXVI-T-84073310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840733'}), (b {id: 'SXVI-T-84073320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840733'}), (b {id: 'SXVI-T-84073390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-840734'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073440'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073450'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073460'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073471'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073472'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073473'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073491'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073492'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073493'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073494'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073495'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840734'}), (b {id: 'SXVI-T-84073499'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8407'}), (b {id: 'SXVI-T-840790'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840790'}), (b {id: 'SXVI-T-84079010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840790'}), (b {id: 'SXVI-T-84079020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840790'}), (b {id: 'SXVI-T-84079090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8408'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8408'}), (b {id: 'SXVI-T-840810'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840810'}), (b {id: 'SXVI-T-84081010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840810'}), (b {id: 'SXVI-T-84081020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840810'}), (b {id: 'SXVI-T-84081030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840810'}), (b {id: 'SXVI-T-84081090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8408'}), (b {id: 'SXVI-T-840820'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082023'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840820'}), (b {id: 'SXVI-T-84082096'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8408'}), (b {id: 'SXVI-T-840890'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840890'}), (b {id: 'SXVI-T-84089010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840890'}), (b {id: 'SXVI-T-84089051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840890'}), (b {id: 'SXVI-T-84089052'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840890'}), (b {id: 'SXVI-T-84089059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840890'}), (b {id: 'SXVI-T-84089091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840890'}), (b {id: 'SXVI-T-84089092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840890'}), (b {id: 'SXVI-T-84089099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8409'}), (b {id: 'SXVI-T-84091000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8409'}), (b {id: 'SXVI-T-840991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099112'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099113'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099114'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099115'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099116'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099117'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099118'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099121'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099122'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099123'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099124'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099126'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099128'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099129'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099131'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099132'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099134'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099135'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099137'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099138'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099139'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099141'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099142'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099143'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099144'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099145'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099146'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099147'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099148'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099149'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099151'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099152'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099153'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099154'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099155'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099159'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099161'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099162'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099163'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099164'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099169'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099171'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099172'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099173'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099174'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099176'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099177'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099178'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840991'}), (b {id: 'SXVI-T-84099179'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8409'}), (b {id: 'SXVI-T-840999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099912'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099913'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099914'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099915'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099916'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099917'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099918'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099922'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099923'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099924'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099925'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099926'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099927'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099931'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099932'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099934'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099936'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099937'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099938'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099941'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099942'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099943'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099944'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099945'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099946'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099947'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099948'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099949'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099951'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099952'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099953'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099954'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099955'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099959'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099961'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099962'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099963'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099964'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099965'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099969'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099971'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099972'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099973'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099974'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099975'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099976'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099977'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099978'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-840999'}), (b {id: 'SXVI-T-84099979'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8410'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8410'}), (b {id: 'SXVI-T-84101100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8410'}), (b {id: 'SXVI-T-84101200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8410'}), (b {id: 'SXVI-T-84101300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8410'}), (b {id: 'SXVI-T-84109000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8411'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84111100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84111200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84112100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84112200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84118100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84118200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84119100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8411'}), (b {id: 'SXVI-T-84119900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8412'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8412'}), (b {id: 'SXVI-T-84121000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8412'}), (b {id: 'SXVI-T-84122100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8412'}), (b {id: 'SXVI-T-84122900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8412'}), (b {id: 'SXVI-T-84123100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8412'}), (b {id: 'SXVI-T-84123900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8412'}), (b {id: 'SXVI-T-84128000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8412'}), (b {id: 'SXVI-T-841290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841290'}), (b {id: 'SXVI-T-84129010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841290'}), (b {id: 'SXVI-T-84129020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841290'}), (b {id: 'SXVI-T-84129090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-84131100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841319'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841319'}), (b {id: 'SXVI-T-84131910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841319'}), (b {id: 'SXVI-T-84131920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841320'}), (b {id: 'SXVI-T-84132010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841320'}), (b {id: 'SXVI-T-84132020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841320'}), (b {id: 'SXVI-T-84132090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841330'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841330'}), (b {id: 'SXVI-T-84133030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841330'}), (b {id: 'SXVI-T-84133040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841330'}), (b {id: 'SXVI-T-84133051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841330'}), (b {id: 'SXVI-T-84133052'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841330'}), (b {id: 'SXVI-T-84133090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-84134000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841350'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841350'}), (b {id: 'SXVI-T-84135031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841350'}), (b {id: 'SXVI-T-84135032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841350'}), (b {id: 'SXVI-T-84135040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841350'}), (b {id: 'SXVI-T-84135090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841360'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841360'}), (b {id: 'SXVI-T-84136031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841360'}), (b {id: 'SXVI-T-84136032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841360'}), (b {id: 'SXVI-T-84136040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841360'}), (b {id: 'SXVI-T-84136090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841370'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137042'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137043'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841370'}), (b {id: 'SXVI-T-84137099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841381'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841381'}), (b {id: 'SXVI-T-84138113'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841381'}), (b {id: 'SXVI-T-84138114'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841381'}), (b {id: 'SXVI-T-84138115'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841381'}), (b {id: 'SXVI-T-84138119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841382'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841382'}), (b {id: 'SXVI-T-84138210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841382'}), (b {id: 'SXVI-T-84138220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-841391'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841391'}), (b {id: 'SXVI-T-84139110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841391'}), (b {id: 'SXVI-T-84139120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841391'}), (b {id: 'SXVI-T-84139130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841391'}), (b {id: 'SXVI-T-84139140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841391'}), (b {id: 'SXVI-T-84139190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8413'}), (b {id: 'SXVI-T-84139200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-84141000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841420'}), (b {id: 'SXVI-T-84142010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841420'}), (b {id: 'SXVI-T-84142090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841430'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841430'}), (b {id: 'SXVI-T-84143040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841430'}), (b {id: 'SXVI-T-84143090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-84144000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841451'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841451'}), (b {id: 'SXVI-T-84145110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841451'}), (b {id: 'SXVI-T-84145191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841451'}), (b {id: 'SXVI-T-84145199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841459'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145941'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145949'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145992'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841459'}), (b {id: 'SXVI-T-84145999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841460'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841460'}), (b {id: 'SXVI-T-84146011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841460'}), (b {id: 'SXVI-T-84146019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841460'}), (b {id: 'SXVI-T-84146091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841460'}), (b {id: 'SXVI-T-84146099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841470'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841470'}), (b {id: 'SXVI-T-84147011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841470'}), (b {id: 'SXVI-T-84147019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841470'}), (b {id: 'SXVI-T-84147021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841470'}), (b {id: 'SXVI-T-84147029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841480'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148042'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148043'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841480'}), (b {id: 'SXVI-T-84148090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8414'}), (b {id: 'SXVI-T-841490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149042'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149060'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149070'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149080'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841490'}), (b {id: 'SXVI-T-84149090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8415'}), (b {id: 'SXVI-T-841510'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841510'}), (b {id: 'SXVI-T-84151020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841510'}), (b {id: 'SXVI-T-84151030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841510'}), (b {id: 'SXVI-T-84151090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8415'}), (b {id: 'SXVI-T-841520'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841520'}), (b {id: 'SXVI-T-84152010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841520'}), (b {id: 'SXVI-T-84152090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8415'}), (b {id: 'SXVI-T-841581'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158112'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158121'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158129'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158131'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158139'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158195'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158196'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158197'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158198'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841581'}), (b {id: 'SXVI-T-84158199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8415'}), (b {id: 'SXVI-T-841582'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158221'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158229'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158231'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158239'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158291'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841582'}), (b {id: 'SXVI-T-84158299'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8415'}), (b {id: 'SXVI-T-841583'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158311'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158319'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158321'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158329'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158331'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158339'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158391'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841583'}), (b {id: 'SXVI-T-84158399'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8415'}), (b {id: 'SXVI-T-841590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159014'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159015'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159024'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159025'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159026'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159034'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159035'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159036'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159044'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159045'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159046'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841590'}), (b {id: 'SXVI-T-84159049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8416'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8416'}), (b {id: 'SXVI-T-84161000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8416'}), (b {id: 'SXVI-T-84162000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8416'}), (b {id: 'SXVI-T-84163000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8416'}), (b {id: 'SXVI-T-84169000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8417'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8417'}), (b {id: 'SXVI-T-84171000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8417'}), (b {id: 'SXVI-T-84172000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8417'}), (b {id: 'SXVI-T-841780'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841780'}), (b {id: 'SXVI-T-84178010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841780'}), (b {id: 'SXVI-T-84178090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8417'}), (b {id: 'SXVI-T-84179000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-841810'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841810'}), (b {id: 'SXVI-T-84181031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841810'}), (b {id: 'SXVI-T-84181032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841810'}), (b {id: 'SXVI-T-84181039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841810'}), (b {id: 'SXVI-T-84181040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841810'}), (b {id: 'SXVI-T-84181091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841810'}), (b {id: 'SXVI-T-84181099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-841821'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841821'}), (b {id: 'SXVI-T-84182110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841821'}), (b {id: 'SXVI-T-84182190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-84182900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-841830'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841830'}), (b {id: 'SXVI-T-84183010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841830'}), (b {id: 'SXVI-T-84183090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-841840'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841840'}), (b {id: 'SXVI-T-84184010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841840'}), (b {id: 'SXVI-T-84184090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-841850'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841850'}), (b {id: 'SXVI-T-84185011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841850'}), (b {id: 'SXVI-T-84185019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841850'}), (b {id: 'SXVI-T-84185091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841850'}), (b {id: 'SXVI-T-84185099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-84186100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-841869'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841869'}), (b {id: 'SXVI-T-84186910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841869'}), (b {id: 'SXVI-T-84186930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841869'}), (b {id: 'SXVI-T-84186941'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841869'}), (b {id: 'SXVI-T-84186949'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841869'}), (b {id: 'SXVI-T-84186950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841869'}), (b {id: 'SXVI-T-84186990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-84189100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8418'}), (b {id: 'SXVI-T-841899'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841899'}), (b {id: 'SXVI-T-84189910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841899'}), (b {id: 'SXVI-T-84189940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841899'}), (b {id: 'SXVI-T-84189990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841911'}), (b {id: 'SXVI-T-84191110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841911'}), (b {id: 'SXVI-T-84191190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-84191200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841919'}), (b {id: 'SXVI-T-84191910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841919'}), (b {id: 'SXVI-T-84191990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-84192000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841933'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841933'}), (b {id: 'SXVI-T-84193310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841933'}), (b {id: 'SXVI-T-84193390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841934'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841934'}), (b {id: 'SXVI-T-84193410'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841934'}), (b {id: 'SXVI-T-84193420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841934'}), (b {id: 'SXVI-T-84193490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841935'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841935'}), (b {id: 'SXVI-T-84193510'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841935'}), (b {id: 'SXVI-T-84193520'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841939'}), (b {id: 'SXVI-T-84193930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841939'}), (b {id: 'SXVI-T-84193990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841940'}), (b {id: 'SXVI-T-84194010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841940'}), (b {id: 'SXVI-T-84194020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841950'}), (b {id: 'SXVI-T-84195010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841950'}), (b {id: 'SXVI-T-84195020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841950'}), (b {id: 'SXVI-T-84195091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841950'}), (b {id: 'SXVI-T-84195092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-84196000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841981'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841981'}), (b {id: 'SXVI-T-84198110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841981'}), (b {id: 'SXVI-T-84198120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841989'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841989'}), (b {id: 'SXVI-T-84198913'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841989'}), (b {id: 'SXVI-T-84198919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841989'}), (b {id: 'SXVI-T-84198920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8419'}), (b {id: 'SXVI-T-841990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841990'}), (b {id: 'SXVI-T-84199012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841990'}), (b {id: 'SXVI-T-84199013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841990'}), (b {id: 'SXVI-T-84199019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841990'}), (b {id: 'SXVI-T-84199022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-841990'}), (b {id: 'SXVI-T-84199029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8420'}), (b {id: 'SXVI-T-842010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842010'}), (b {id: 'SXVI-T-84201010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842010'}), (b {id: 'SXVI-T-84201020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842010'}), (b {id: 'SXVI-T-84201090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8420'}), (b {id: 'SXVI-T-842091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842091'}), (b {id: 'SXVI-T-84209110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842091'}), (b {id: 'SXVI-T-84209190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8420'}), (b {id: 'SXVI-T-842099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842099'}), (b {id: 'SXVI-T-84209910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842099'}), (b {id: 'SXVI-T-84209990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-84211100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-84211200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842119'}), (b {id: 'SXVI-T-84211910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842119'}), (b {id: 'SXVI-T-84211990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842121'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842121'}), (b {id: 'SXVI-T-84212111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842121'}), (b {id: 'SXVI-T-84212119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842121'}), (b {id: 'SXVI-T-84212122'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842121'}), (b {id: 'SXVI-T-84212123'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842122'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842122'}), (b {id: 'SXVI-T-84212230'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842122'}), (b {id: 'SXVI-T-84212290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842123'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842123'}), (b {id: 'SXVI-T-84212311'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842123'}), (b {id: 'SXVI-T-84212319'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842123'}), (b {id: 'SXVI-T-84212321'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842123'}), (b {id: 'SXVI-T-84212329'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842123'}), (b {id: 'SXVI-T-84212391'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842123'}), (b {id: 'SXVI-T-84212399'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842129'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842129'}), (b {id: 'SXVI-T-84212910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842129'}), (b {id: 'SXVI-T-84212920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842129'}), (b {id: 'SXVI-T-84212930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842129'}), (b {id: 'SXVI-T-84212940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842129'}), (b {id: 'SXVI-T-84212950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842129'}), (b {id: 'SXVI-T-84212960'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842129'}), (b {id: 'SXVI-T-84212990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842131'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842131'}), (b {id: 'SXVI-T-84213110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842131'}), (b {id: 'SXVI-T-84213120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842131'}), (b {id: 'SXVI-T-84213190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-84213200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842139'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842139'}), (b {id: 'SXVI-T-84213920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842139'}), (b {id: 'SXVI-T-84213930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842139'}), (b {id: 'SXVI-T-84213990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842191'}), (b {id: 'SXVI-T-84219110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842191'}), (b {id: 'SXVI-T-84219120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842191'}), (b {id: 'SXVI-T-84219190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8421'}), (b {id: 'SXVI-T-842199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219960'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219970'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219994'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219996'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219997'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842199'}), (b {id: 'SXVI-T-84219999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8422'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8422'}), (b {id: 'SXVI-T-84221100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8422'}), (b {id: 'SXVI-T-84221900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8422'}), (b {id: 'SXVI-T-84222000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8422'}), (b {id: 'SXVI-T-84223000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8422'}), (b {id: 'SXVI-T-84224000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8422'}), (b {id: 'SXVI-T-842290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842290'}), (b {id: 'SXVI-T-84229010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842290'}), (b {id: 'SXVI-T-84229090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8423'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8423'}), (b {id: 'SXVI-T-842310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842310'}), (b {id: 'SXVI-T-84231010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842310'}), (b {id: 'SXVI-T-84231020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8423'}), (b {id: 'SXVI-T-842320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842320'}), (b {id: 'SXVI-T-84232010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842320'}), (b {id: 'SXVI-T-84232090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8423'}), (b {id: 'SXVI-T-842330'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842330'}), (b {id: 'SXVI-T-84233010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842330'}), (b {id: 'SXVI-T-84233090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8423'}), (b {id: 'SXVI-T-842381'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842381'}), (b {id: 'SXVI-T-84238110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842381'}), (b {id: 'SXVI-T-84238190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8423'}), (b {id: 'SXVI-T-842382'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842382'}), (b {id: 'SXVI-T-84238231'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842382'}), (b {id: 'SXVI-T-84238232'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842382'}), (b {id: 'SXVI-T-84238239'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842382'}), (b {id: 'SXVI-T-84238241'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842382'}), (b {id: 'SXVI-T-84238242'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842382'}), (b {id: 'SXVI-T-84238249'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8423'}), (b {id: 'SXVI-T-842389'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842389'}), (b {id: 'SXVI-T-84238910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842389'}), (b {id: 'SXVI-T-84238990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8423'}), (b {id: 'SXVI-T-842390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842390'}), (b {id: 'SXVI-T-84239010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842390'}), (b {id: 'SXVI-T-84239030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842390'}), (b {id: 'SXVI-T-84239040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-842410'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842410'}), (b {id: 'SXVI-T-84241010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842410'}), (b {id: 'SXVI-T-84241090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-842420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842420'}), (b {id: 'SXVI-T-84242011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842420'}), (b {id: 'SXVI-T-84242019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842420'}), (b {id: 'SXVI-T-84242021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842420'}), (b {id: 'SXVI-T-84242029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-84243000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-842441'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842441'}), (b {id: 'SXVI-T-84244110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842441'}), (b {id: 'SXVI-T-84244120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842441'}), (b {id: 'SXVI-T-84244190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-842449'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842449'}), (b {id: 'SXVI-T-84244910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842449'}), (b {id: 'SXVI-T-84244920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-842482'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842482'}), (b {id: 'SXVI-T-84248210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842482'}), (b {id: 'SXVI-T-84248220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842482'}), (b {id: 'SXVI-T-84248230'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-842489'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842489'}), (b {id: 'SXVI-T-84248910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842489'}), (b {id: 'SXVI-T-84248920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842489'}), (b {id: 'SXVI-T-84248940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842489'}), (b {id: 'SXVI-T-84248950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842489'}), (b {id: 'SXVI-T-84248990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8424'}), (b {id: 'SXVI-T-842490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249023'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249024'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249096'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842490'}), (b {id: 'SXVI-T-84249099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8425'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8425'}), (b {id: 'SXVI-T-84251100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8425'}), (b {id: 'SXVI-T-84251900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8425'}), (b {id: 'SXVI-T-84253100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8425'}), (b {id: 'SXVI-T-84253900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8425'}), (b {id: 'SXVI-T-84254100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8425'}), (b {id: 'SXVI-T-842542'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842542'}), (b {id: 'SXVI-T-84254210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842542'}), (b {id: 'SXVI-T-84254290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8425'}), (b {id: 'SXVI-T-842549'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842549'}), (b {id: 'SXVI-T-84254910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842549'}), (b {id: 'SXVI-T-84254920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8426'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84261100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84261200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-842619'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842619'}), (b {id: 'SXVI-T-84261920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842619'}), (b {id: 'SXVI-T-84261930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842619'}), (b {id: 'SXVI-T-84261990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84262000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84263000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84264100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84264900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84269100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8426'}), (b {id: 'SXVI-T-84269900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8427'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8427'}), (b {id: 'SXVI-T-84271000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8427'}), (b {id: 'SXVI-T-84272000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8427'}), (b {id: 'SXVI-T-84279000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8428'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-842810'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842810'}), (b {id: 'SXVI-T-84281031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842810'}), (b {id: 'SXVI-T-84281039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842810'}), (b {id: 'SXVI-T-84281040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-842820'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842820'}), (b {id: 'SXVI-T-84282010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842820'}), (b {id: 'SXVI-T-84282090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-84283100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-842832'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842832'}), (b {id: 'SXVI-T-84283210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842832'}), (b {id: 'SXVI-T-84283290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-842833'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842833'}), (b {id: 'SXVI-T-84283310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842833'}), (b {id: 'SXVI-T-84283390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-842839'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842839'}), (b {id: 'SXVI-T-84283910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842839'}), (b {id: 'SXVI-T-84283990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-84284000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-84286000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-84287000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8428'}), (b {id: 'SXVI-T-842890'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842890'}), (b {id: 'SXVI-T-84289020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842890'}), (b {id: 'SXVI-T-84289030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842890'}), (b {id: 'SXVI-T-84289090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8429'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-84291100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-84291900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-84292000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-84293000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-842940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842940'}), (b {id: 'SXVI-T-84294030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842940'}), (b {id: 'SXVI-T-84294040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842940'}), (b {id: 'SXVI-T-84294050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-842940'}), (b {id: 'SXVI-T-84294090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-84295100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-84295200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8429'}), (b {id: 'SXVI-T-84295900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8430'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84301000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84302000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84303100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84303900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84304100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-843049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843049'}), (b {id: 'SXVI-T-84304910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843049'}), (b {id: 'SXVI-T-84304990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84305000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84306100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8430'}), (b {id: 'SXVI-T-84306900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-843110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843110'}), (b {id: 'SXVI-T-84311013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843110'}), (b {id: 'SXVI-T-84311019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843110'}), (b {id: 'SXVI-T-84311022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843110'}), (b {id: 'SXVI-T-84311029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-843120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843120'}), (b {id: 'SXVI-T-84312010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843120'}), (b {id: 'SXVI-T-84312090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-843131'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843131'}), (b {id: 'SXVI-T-84313110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843131'}), (b {id: 'SXVI-T-84313120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-843139'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843139'}), (b {id: 'SXVI-T-84313910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843139'}), (b {id: 'SXVI-T-84313940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843139'}), (b {id: 'SXVI-T-84313950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843139'}), (b {id: 'SXVI-T-84313990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-843141'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843141'}), (b {id: 'SXVI-T-84314110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843141'}), (b {id: 'SXVI-T-84314190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-84314200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-84314300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8431'}), (b {id: 'SXVI-T-843149'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843149'}), (b {id: 'SXVI-T-84314910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843149'}), (b {id: 'SXVI-T-84314920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843149'}), (b {id: 'SXVI-T-84314940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843149'}), (b {id: 'SXVI-T-84314950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843149'}), (b {id: 'SXVI-T-84314960'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843149'}), (b {id: 'SXVI-T-84314990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8432'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-84321000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-84322100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-84322900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-84323100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-84323900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-84324100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-84324200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-843280'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843280'}), (b {id: 'SXVI-T-84328010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843280'}), (b {id: 'SXVI-T-84328020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843280'}), (b {id: 'SXVI-T-84328090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8432'}), (b {id: 'SXVI-T-843290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843290'}), (b {id: 'SXVI-T-84329010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843290'}), (b {id: 'SXVI-T-84329020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843290'}), (b {id: 'SXVI-T-84329090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8433'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-84331100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-843319'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843319'}), (b {id: 'SXVI-T-84331910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843319'}), (b {id: 'SXVI-T-84331990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-84332000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-84333000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-84334000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-84335100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-84335200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-84335300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-843359'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843359'}), (b {id: 'SXVI-T-84335920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843359'}), (b {id: 'SXVI-T-84335990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-843360'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843360'}), (b {id: 'SXVI-T-84336010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843360'}), (b {id: 'SXVI-T-84336020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8433'}), (b {id: 'SXVI-T-843390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843390'}), (b {id: 'SXVI-T-84339010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843390'}), (b {id: 'SXVI-T-84339020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843390'}), (b {id: 'SXVI-T-84339030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843390'}), (b {id: 'SXVI-T-84339090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8434'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8434'}), (b {id: 'SXVI-T-84341000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8434'}), (b {id: 'SXVI-T-84342000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8434'}), (b {id: 'SXVI-T-84349000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8435'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8435'}), (b {id: 'SXVI-T-843510'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843510'}), (b {id: 'SXVI-T-84351010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843510'}), (b {id: 'SXVI-T-84351020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8435'}), (b {id: 'SXVI-T-843590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843590'}), (b {id: 'SXVI-T-84359010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843590'}), (b {id: 'SXVI-T-84359020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8436'}), (b {id: 'SXVI-T-843610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843610'}), (b {id: 'SXVI-T-84361010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843610'}), (b {id: 'SXVI-T-84361020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8436'}), (b {id: 'SXVI-T-843621'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843621'}), (b {id: 'SXVI-T-84362110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843621'}), (b {id: 'SXVI-T-84362120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8436'}), (b {id: 'SXVI-T-843629'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843629'}), (b {id: 'SXVI-T-84362910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843629'}), (b {id: 'SXVI-T-84362920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8436'}), (b {id: 'SXVI-T-843680'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843680'}), (b {id: 'SXVI-T-84368011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843680'}), (b {id: 'SXVI-T-84368019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843680'}), (b {id: 'SXVI-T-84368021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843680'}), (b {id: 'SXVI-T-84368029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8436'}), (b {id: 'SXVI-T-84369100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8436'}), (b {id: 'SXVI-T-843699'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843699'}), (b {id: 'SXVI-T-84369911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843699'}), (b {id: 'SXVI-T-84369919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843699'}), (b {id: 'SXVI-T-84369921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843699'}), (b {id: 'SXVI-T-84369929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8437'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8437'}), (b {id: 'SXVI-T-843710'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843710'}), (b {id: 'SXVI-T-84371010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843710'}), (b {id: 'SXVI-T-84371020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843710'}), (b {id: 'SXVI-T-84371030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843710'}), (b {id: 'SXVI-T-84371040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8437'}), (b {id: 'SXVI-T-843780'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378061'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843780'}), (b {id: 'SXVI-T-84378069'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8437'}), (b {id: 'SXVI-T-843790'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843790'}), (b {id: 'SXVI-T-84379011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843790'}), (b {id: 'SXVI-T-84379019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843790'}), (b {id: 'SXVI-T-84379021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843790'}), (b {id: 'SXVI-T-84379029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8438'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-84381000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-843820'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843820'}), (b {id: 'SXVI-T-84382010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843820'}), (b {id: 'SXVI-T-84382020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-843830'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843830'}), (b {id: 'SXVI-T-84383010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843830'}), (b {id: 'SXVI-T-84383020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-84384000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-84385000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-84386000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-843880'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843880'}), (b {id: 'SXVI-T-84388011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843880'}), (b {id: 'SXVI-T-84388012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843880'}), (b {id: 'SXVI-T-84388021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843880'}), (b {id: 'SXVI-T-84388022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843880'}), (b {id: 'SXVI-T-84388091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843880'}), (b {id: 'SXVI-T-84388092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8438'}), (b {id: 'SXVI-T-843890'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843890'}), (b {id: 'SXVI-T-84389011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843890'}), (b {id: 'SXVI-T-84389012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843890'}), (b {id: 'SXVI-T-84389019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843890'}), (b {id: 'SXVI-T-84389021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843890'}), (b {id: 'SXVI-T-84389022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-843890'}), (b {id: 'SXVI-T-84389029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8439'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8439'}), (b {id: 'SXVI-T-84391000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8439'}), (b {id: 'SXVI-T-84392000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8439'}), (b {id: 'SXVI-T-84393000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8439'}), (b {id: 'SXVI-T-84399100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8439'}), (b {id: 'SXVI-T-84399900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8440'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8440'}), (b {id: 'SXVI-T-844010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844010'}), (b {id: 'SXVI-T-84401010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844010'}), (b {id: 'SXVI-T-84401020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8440'}), (b {id: 'SXVI-T-84409000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8441'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8441'}), (b {id: 'SXVI-T-844110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844110'}), (b {id: 'SXVI-T-84411010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844110'}), (b {id: 'SXVI-T-84411020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8441'}), (b {id: 'SXVI-T-84412000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8441'}), (b {id: 'SXVI-T-84413000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8441'}), (b {id: 'SXVI-T-84414000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8441'}), (b {id: 'SXVI-T-844180'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844180'}), (b {id: 'SXVI-T-84418010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844180'}), (b {id: 'SXVI-T-84418020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8441'}), (b {id: 'SXVI-T-84419000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8442'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8442'}), (b {id: 'SXVI-T-84423000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8442'}), (b {id: 'SXVI-T-84424000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8442'}), (b {id: 'SXVI-T-84425000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431500'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431600'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431700'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84431900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-844331'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433121'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433129'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433131'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433139'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844331'}), (b {id: 'SXVI-T-84433199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-844332'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433221'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433229'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433231'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433239'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433240'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433250'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433260'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844332'}), (b {id: 'SXVI-T-84433290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-844339'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844339'}), (b {id: 'SXVI-T-84433910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844339'}), (b {id: 'SXVI-T-84433920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844339'}), (b {id: 'SXVI-T-84433930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844339'}), (b {id: 'SXVI-T-84433940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844339'}), (b {id: 'SXVI-T-84433990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-84439100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8443'}), (b {id: 'SXVI-T-844399'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844399'}), (b {id: 'SXVI-T-84439910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844399'}), (b {id: 'SXVI-T-84439920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844399'}), (b {id: 'SXVI-T-84439930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844399'}), (b {id: 'SXVI-T-84439990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8444'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8444'}), (b {id: 'SXVI-T-84440010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8444'}), (b {id: 'SXVI-T-84440020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8445'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-844511'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844511'}), (b {id: 'SXVI-T-84451110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844511'}), (b {id: 'SXVI-T-84451120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-84451200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-84451300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-844519'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844519'}), (b {id: 'SXVI-T-84451930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844519'}), (b {id: 'SXVI-T-84451940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844519'}), (b {id: 'SXVI-T-84451950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-844520'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844520'}), (b {id: 'SXVI-T-84452010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844520'}), (b {id: 'SXVI-T-84452020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-844530'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844530'}), (b {id: 'SXVI-T-84453010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844530'}), (b {id: 'SXVI-T-84453020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-844540'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844540'}), (b {id: 'SXVI-T-84454010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844540'}), (b {id: 'SXVI-T-84454020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8445'}), (b {id: 'SXVI-T-844590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844590'}), (b {id: 'SXVI-T-84459010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844590'}), (b {id: 'SXVI-T-84459020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8446'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8446'}), (b {id: 'SXVI-T-844610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844610'}), (b {id: 'SXVI-T-84461010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844610'}), (b {id: 'SXVI-T-84461020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8446'}), (b {id: 'SXVI-T-84462100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8446'}), (b {id: 'SXVI-T-84462900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8446'}), (b {id: 'SXVI-T-84463000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8447'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8447'}), (b {id: 'SXVI-T-84471100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8447'}), (b {id: 'SXVI-T-84471200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8447'}), (b {id: 'SXVI-T-844720'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844720'}), (b {id: 'SXVI-T-84472010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844720'}), (b {id: 'SXVI-T-84472020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8447'}), (b {id: 'SXVI-T-844790'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844790'}), (b {id: 'SXVI-T-84479010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844790'}), (b {id: 'SXVI-T-84479020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-844811'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844811'}), (b {id: 'SXVI-T-84481110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844811'}), (b {id: 'SXVI-T-84481120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-844819'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844819'}), (b {id: 'SXVI-T-84481910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844819'}), (b {id: 'SXVI-T-84481920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84482000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84483100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84483200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84483300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84483900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84484200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-844849'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844849'}), (b {id: 'SXVI-T-84484911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844849'}), (b {id: 'SXVI-T-84484912'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-844849'}), (b {id: 'SXVI-T-84484990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84485100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8448'}), (b {id: 'SXVI-T-84485900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8449'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8449'}), (b {id: 'SXVI-T-84490000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8450'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8450'}), (b {id: 'SXVI-T-845011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845011'}), (b {id: 'SXVI-T-84501110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845011'}), (b {id: 'SXVI-T-84501190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8450'}), (b {id: 'SXVI-T-845012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845012'}), (b {id: 'SXVI-T-84501210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845012'}), (b {id: 'SXVI-T-84501290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8450'}), (b {id: 'SXVI-T-845019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845019'}), (b {id: 'SXVI-T-84501911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845019'}), (b {id: 'SXVI-T-84501919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845019'}), (b {id: 'SXVI-T-84501991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845019'}), (b {id: 'SXVI-T-84501999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8450'}), (b {id: 'SXVI-T-84502000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8450'}), (b {id: 'SXVI-T-845090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845090'}), (b {id: 'SXVI-T-84509010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845090'}), (b {id: 'SXVI-T-84509020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8451'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-84511000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-84512100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-84512900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-845130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845130'}), (b {id: 'SXVI-T-84513010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845130'}), (b {id: 'SXVI-T-84513090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-84514000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-84515000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-84518000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8451'}), (b {id: 'SXVI-T-845190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845190'}), (b {id: 'SXVI-T-84519010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845190'}), (b {id: 'SXVI-T-84519090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8452'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8452'}), (b {id: 'SXVI-T-84521000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8452'}), (b {id: 'SXVI-T-84522100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8452'}), (b {id: 'SXVI-T-84522900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8452'}), (b {id: 'SXVI-T-84523000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8452'}), (b {id: 'SXVI-T-845290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845290'}), (b {id: 'SXVI-T-84529011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845290'}), (b {id: 'SXVI-T-84529012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845290'}), (b {id: 'SXVI-T-84529019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845290'}), (b {id: 'SXVI-T-84529091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845290'}), (b {id: 'SXVI-T-84529092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845290'}), (b {id: 'SXVI-T-84529099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8453'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8453'}), (b {id: 'SXVI-T-845310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845310'}), (b {id: 'SXVI-T-84531010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845310'}), (b {id: 'SXVI-T-84531020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8453'}), (b {id: 'SXVI-T-845320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845320'}), (b {id: 'SXVI-T-84532010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845320'}), (b {id: 'SXVI-T-84532020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8453'}), (b {id: 'SXVI-T-845380'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845380'}), (b {id: 'SXVI-T-84538010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845380'}), (b {id: 'SXVI-T-84538020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8453'}), (b {id: 'SXVI-T-84539000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8454'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8454'}), (b {id: 'SXVI-T-84541000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8454'}), (b {id: 'SXVI-T-84542000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8454'}), (b {id: 'SXVI-T-84543000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8454'}), (b {id: 'SXVI-T-84549000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8455'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8455'}), (b {id: 'SXVI-T-84551000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8455'}), (b {id: 'SXVI-T-84552100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8455'}), (b {id: 'SXVI-T-84552200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8455'}), (b {id: 'SXVI-T-84553000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8455'}), (b {id: 'SXVI-T-84559000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8456'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8456'}), (b {id: 'SXVI-T-845611'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845611'}), (b {id: 'SXVI-T-84561110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845611'}), (b {id: 'SXVI-T-84561190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8456'}), (b {id: 'SXVI-T-845612'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845612'}), (b {id: 'SXVI-T-84561210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845612'}), (b {id: 'SXVI-T-84561290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8456'}), (b {id: 'SXVI-T-84562000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8456'}), (b {id: 'SXVI-T-84563000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8456'}), (b {id: 'SXVI-T-845640'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845640'}), (b {id: 'SXVI-T-84564010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845640'}), (b {id: 'SXVI-T-84564020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845640'}), (b {id: 'SXVI-T-84564090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8456'}), (b {id: 'SXVI-T-84565000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8456'}), (b {id: 'SXVI-T-845690'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845690'}), (b {id: 'SXVI-T-84569020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845690'}), (b {id: 'SXVI-T-84569090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8457'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8457'}), (b {id: 'SXVI-T-845710'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845710'}), (b {id: 'SXVI-T-84571010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845710'}), (b {id: 'SXVI-T-84571090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8457'}), (b {id: 'SXVI-T-84572000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8457'}), (b {id: 'SXVI-T-84573000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8458'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8458'}), (b {id: 'SXVI-T-845811'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845811'}), (b {id: 'SXVI-T-84581110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845811'}), (b {id: 'SXVI-T-84581190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8458'}), (b {id: 'SXVI-T-845819'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845819'}), (b {id: 'SXVI-T-84581910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845819'}), (b {id: 'SXVI-T-84581990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8458'}), (b {id: 'SXVI-T-84589100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8458'}), (b {id: 'SXVI-T-845899'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845899'}), (b {id: 'SXVI-T-84589910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845899'}), (b {id: 'SXVI-T-84589990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8459'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-84591000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-84592100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-845929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845929'}), (b {id: 'SXVI-T-84592910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845929'}), (b {id: 'SXVI-T-84592920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-84593100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-845939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845939'}), (b {id: 'SXVI-T-84593910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845939'}), (b {id: 'SXVI-T-84593920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-84594100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-845949'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845949'}), (b {id: 'SXVI-T-84594910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845949'}), (b {id: 'SXVI-T-84594920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-84595100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-845959'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845959'}), (b {id: 'SXVI-T-84595910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845959'}), (b {id: 'SXVI-T-84595920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-84596100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-845969'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845969'}), (b {id: 'SXVI-T-84596910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845969'}), (b {id: 'SXVI-T-84596920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8459'}), (b {id: 'SXVI-T-845970'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845970'}), (b {id: 'SXVI-T-84597010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-845970'}), (b {id: 'SXVI-T-84597020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8460'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-84601200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-84601900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-84602200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-84602300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-84602400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-846029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846029'}), (b {id: 'SXVI-T-84602910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846029'}), (b {id: 'SXVI-T-84602920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-846031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846031'}), (b {id: 'SXVI-T-84603110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846031'}), (b {id: 'SXVI-T-84603190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-846039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846039'}), (b {id: 'SXVI-T-84603910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846039'}), (b {id: 'SXVI-T-84603920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-84604000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8460'}), (b {id: 'SXVI-T-846090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846090'}), (b {id: 'SXVI-T-84609010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846090'}), (b {id: 'SXVI-T-84609020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8461'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8461'}), (b {id: 'SXVI-T-84612000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8461'}), (b {id: 'SXVI-T-84613000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8461'}), (b {id: 'SXVI-T-84614000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8461'}), (b {id: 'SXVI-T-84615000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8461'}), (b {id: 'SXVI-T-846190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846190'}), (b {id: 'SXVI-T-84619020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846190'}), (b {id: 'SXVI-T-84619090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84621100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84621900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-846222'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846222'}), (b {id: 'SXVI-T-84622210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846222'}), (b {id: 'SXVI-T-84622290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84622300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84622400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84622500'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84622600'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84622900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-846232'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846232'}), (b {id: 'SXVI-T-84623210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846232'}), (b {id: 'SXVI-T-84623290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84623300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84623900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84624200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84624900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84625100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-84625900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-846261'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846261'}), (b {id: 'SXVI-T-84626111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846261'}), (b {id: 'SXVI-T-84626119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846261'}), (b {id: 'SXVI-T-84626191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846261'}), (b {id: 'SXVI-T-84626199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-846262'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846262'}), (b {id: 'SXVI-T-84626211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846262'}), (b {id: 'SXVI-T-84626219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846262'}), (b {id: 'SXVI-T-84626291'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846262'}), (b {id: 'SXVI-T-84626299'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-846263'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846263'}), (b {id: 'SXVI-T-84626310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846263'}), (b {id: 'SXVI-T-84626390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-846269'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846269'}), (b {id: 'SXVI-T-84626910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846269'}), (b {id: 'SXVI-T-84626990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8462'}), (b {id: 'SXVI-T-846290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846290'}), (b {id: 'SXVI-T-84629010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846290'}), (b {id: 'SXVI-T-84629090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8463'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8463'}), (b {id: 'SXVI-T-846310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846310'}), (b {id: 'SXVI-T-84631010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846310'}), (b {id: 'SXVI-T-84631020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8463'}), (b {id: 'SXVI-T-846320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846320'}), (b {id: 'SXVI-T-84632010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846320'}), (b {id: 'SXVI-T-84632020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8463'}), (b {id: 'SXVI-T-846330'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846330'}), (b {id: 'SXVI-T-84633010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846330'}), (b {id: 'SXVI-T-84633020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8463'}), (b {id: 'SXVI-T-846390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846390'}), (b {id: 'SXVI-T-84639010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846390'}), (b {id: 'SXVI-T-84639020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8464'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8464'}), (b {id: 'SXVI-T-846410'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846410'}), (b {id: 'SXVI-T-84641010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846410'}), (b {id: 'SXVI-T-84641020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8464'}), (b {id: 'SXVI-T-846420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846420'}), (b {id: 'SXVI-T-84642010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846420'}), (b {id: 'SXVI-T-84642020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8464'}), (b {id: 'SXVI-T-846490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846490'}), (b {id: 'SXVI-T-84649010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846490'}), (b {id: 'SXVI-T-84649020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8465'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-84651000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-84652000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-846591'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846591'}), (b {id: 'SXVI-T-84659110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846591'}), (b {id: 'SXVI-T-84659190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-846592'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846592'}), (b {id: 'SXVI-T-84659210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846592'}), (b {id: 'SXVI-T-84659290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-846593'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846593'}), (b {id: 'SXVI-T-84659310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846593'}), (b {id: 'SXVI-T-84659320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-84659400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-846595'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846595'}), (b {id: 'SXVI-T-84659510'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846595'}), (b {id: 'SXVI-T-84659590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-84659600'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8465'}), (b {id: 'SXVI-T-846599'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846599'}), (b {id: 'SXVI-T-84659910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846599'}), (b {id: 'SXVI-T-84659950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846599'}), (b {id: 'SXVI-T-84659960'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846599'}), (b {id: 'SXVI-T-84659990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8466'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8466'}), (b {id: 'SXVI-T-846610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846610'}), (b {id: 'SXVI-T-84661010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846610'}), (b {id: 'SXVI-T-84661090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8466'}), (b {id: 'SXVI-T-846620'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846620'}), (b {id: 'SXVI-T-84662010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846620'}), (b {id: 'SXVI-T-84662090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8466'}), (b {id: 'SXVI-T-84663000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8466'}), (b {id: 'SXVI-T-84669100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8466'}), (b {id: 'SXVI-T-84669200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8466'}), (b {id: 'SXVI-T-846693'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846693'}), (b {id: 'SXVI-T-84669330'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846693'}), (b {id: 'SXVI-T-84669340'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846693'}), (b {id: 'SXVI-T-84669390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8466'}), (b {id: 'SXVI-T-84669400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8467'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84671100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84671900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84672100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84672200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84672900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84678100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84678900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-846791'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846791'}), (b {id: 'SXVI-T-84679110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846791'}), (b {id: 'SXVI-T-84679190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-84679200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8467'}), (b {id: 'SXVI-T-846799'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846799'}), (b {id: 'SXVI-T-84679910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846799'}), (b {id: 'SXVI-T-84679990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8468'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8468'}), (b {id: 'SXVI-T-84681000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8468'}), (b {id: 'SXVI-T-846820'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846820'}), (b {id: 'SXVI-T-84682010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846820'}), (b {id: 'SXVI-T-84682090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8468'}), (b {id: 'SXVI-T-84688000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8468'}), (b {id: 'SXVI-T-846890'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846890'}), (b {id: 'SXVI-T-84689020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-846890'}), (b {id: 'SXVI-T-84689090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8470'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8470'}), (b {id: 'SXVI-T-84701000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8470'}), (b {id: 'SXVI-T-84702100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8470'}), (b {id: 'SXVI-T-84702900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8470'}), (b {id: 'SXVI-T-84703000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8470'}), (b {id: 'SXVI-T-84705000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8470'}), (b {id: 'SXVI-T-847090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847090'}), (b {id: 'SXVI-T-84709010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847090'}), (b {id: 'SXVI-T-84709090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8471'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847130'}), (b {id: 'SXVI-T-84713020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847130'}), (b {id: 'SXVI-T-84713090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847141'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847141'}), (b {id: 'SXVI-T-84714110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847141'}), (b {id: 'SXVI-T-84714190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847149'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847149'}), (b {id: 'SXVI-T-84714910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847149'}), (b {id: 'SXVI-T-84714990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847150'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847150'}), (b {id: 'SXVI-T-84715010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847150'}), (b {id: 'SXVI-T-84715090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847160'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847160'}), (b {id: 'SXVI-T-84716030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847160'}), (b {id: 'SXVI-T-84716040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847160'}), (b {id: 'SXVI-T-84716090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847170'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847170'}), (b {id: 'SXVI-T-84717020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847170'}), (b {id: 'SXVI-T-84717030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847170'}), (b {id: 'SXVI-T-84717040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847170'}), (b {id: 'SXVI-T-84717090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847180'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847180'}), (b {id: 'SXVI-T-84718010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847180'}), (b {id: 'SXVI-T-84718070'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847180'}), (b {id: 'SXVI-T-84718090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8471'}), (b {id: 'SXVI-T-847190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847190'}), (b {id: 'SXVI-T-84719010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847190'}), (b {id: 'SXVI-T-84719030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847190'}), (b {id: 'SXVI-T-84719040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847190'}), (b {id: 'SXVI-T-84719090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8472'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8472'}), (b {id: 'SXVI-T-84721000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8472'}), (b {id: 'SXVI-T-84723000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8472'}), (b {id: 'SXVI-T-847290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847290'}), (b {id: 'SXVI-T-84729010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847290'}), (b {id: 'SXVI-T-84729041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847290'}), (b {id: 'SXVI-T-84729049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847290'}), (b {id: 'SXVI-T-84729050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847290'}), (b {id: 'SXVI-T-84729060'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847290'}), (b {id: 'SXVI-T-84729090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8473'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8473'}), (b {id: 'SXVI-T-84732100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8473'}), (b {id: 'SXVI-T-84732900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8473'}), (b {id: 'SXVI-T-847330'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847330'}), (b {id: 'SXVI-T-84733010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847330'}), (b {id: 'SXVI-T-84733090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8473'}), (b {id: 'SXVI-T-84734000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8473'}), (b {id: 'SXVI-T-847350'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847350'}), (b {id: 'SXVI-T-84735010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847350'}), (b {id: 'SXVI-T-84735090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8474'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8474'}), (b {id: 'SXVI-T-847410'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847410'}), (b {id: 'SXVI-T-84741010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847410'}), (b {id: 'SXVI-T-84741020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8474'}), (b {id: 'SXVI-T-847420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847420'}), (b {id: 'SXVI-T-84742011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847420'}), (b {id: 'SXVI-T-84742019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847420'}), (b {id: 'SXVI-T-84742021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847420'}), (b {id: 'SXVI-T-84742029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8474'}), (b {id: 'SXVI-T-847431'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847431'}), (b {id: 'SXVI-T-84743110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847431'}), (b {id: 'SXVI-T-84743120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8474'}), (b {id: 'SXVI-T-847432'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847432'}), (b {id: 'SXVI-T-84743211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847432'}), (b {id: 'SXVI-T-84743219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847432'}), (b {id: 'SXVI-T-84743221'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847432'}), (b {id: 'SXVI-T-84743229'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8474'}), (b {id: 'SXVI-T-847439'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847439'}), (b {id: 'SXVI-T-84743910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847439'}), (b {id: 'SXVI-T-84743920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8474'}), (b {id: 'SXVI-T-847480'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847480'}), (b {id: 'SXVI-T-84748010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847480'}), (b {id: 'SXVI-T-84748020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8474'}), (b {id: 'SXVI-T-84749000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8475'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8475'}), (b {id: 'SXVI-T-84751000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8475'}), (b {id: 'SXVI-T-84752100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8475'}), (b {id: 'SXVI-T-84752900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8475'}), (b {id: 'SXVI-T-847590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847590'}), (b {id: 'SXVI-T-84759030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847590'}), (b {id: 'SXVI-T-84759090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8476'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8476'}), (b {id: 'SXVI-T-84762100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8476'}), (b {id: 'SXVI-T-84762900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8476'}), (b {id: 'SXVI-T-84768100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8476'}), (b {id: 'SXVI-T-847689'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847689'}), (b {id: 'SXVI-T-84768910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847689'}), (b {id: 'SXVI-T-84768990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8476'}), (b {id: 'SXVI-T-847690'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847690'}), (b {id: 'SXVI-T-84769010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847690'}), (b {id: 'SXVI-T-84769090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8477'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-847710'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847710'}), (b {id: 'SXVI-T-84771010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847710'}), (b {id: 'SXVI-T-84771031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847710'}), (b {id: 'SXVI-T-84771039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-847720'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847720'}), (b {id: 'SXVI-T-84772010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847720'}), (b {id: 'SXVI-T-84772020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-84773000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-847740'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847740'}), (b {id: 'SXVI-T-84774010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847740'}), (b {id: 'SXVI-T-84774020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-84775100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-847759'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847759'}), (b {id: 'SXVI-T-84775910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847759'}), (b {id: 'SXVI-T-84775920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-847780'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847780'}), (b {id: 'SXVI-T-84778010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847780'}), (b {id: 'SXVI-T-84778020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847780'}), (b {id: 'SXVI-T-84778031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847780'}), (b {id: 'SXVI-T-84778039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847780'}), (b {id: 'SXVI-T-84778040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8477'}), (b {id: 'SXVI-T-847790'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847790'}), (b {id: 'SXVI-T-84779010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847790'}), (b {id: 'SXVI-T-84779020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847790'}), (b {id: 'SXVI-T-84779032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847790'}), (b {id: 'SXVI-T-84779039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847790'}), (b {id: 'SXVI-T-84779040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8478'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8478'}), (b {id: 'SXVI-T-847810'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847810'}), (b {id: 'SXVI-T-84781010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847810'}), (b {id: 'SXVI-T-84781020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8478'}), (b {id: 'SXVI-T-84789000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8479'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-847910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847910'}), (b {id: 'SXVI-T-84791010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847910'}), (b {id: 'SXVI-T-84791020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-847920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847920'}), (b {id: 'SXVI-T-84792010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847920'}), (b {id: 'SXVI-T-84792020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-84793000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-847940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847940'}), (b {id: 'SXVI-T-84794010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847940'}), (b {id: 'SXVI-T-84794020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-84795000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-84796000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-84797100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-84797900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-847981'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847981'}), (b {id: 'SXVI-T-84798110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847981'}), (b {id: 'SXVI-T-84798120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-847982'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847982'}), (b {id: 'SXVI-T-84798210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847982'}), (b {id: 'SXVI-T-84798220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-84798300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-847989'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847989'}), (b {id: 'SXVI-T-84798910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847989'}), (b {id: 'SXVI-T-84798950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847989'}), (b {id: 'SXVI-T-84798961'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847989'}), (b {id: 'SXVI-T-84798969'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847989'}), (b {id: 'SXVI-T-84798970'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8479'}), (b {id: 'SXVI-T-847990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847990'}), (b {id: 'SXVI-T-84799010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847990'}), (b {id: 'SXVI-T-84799050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-847990'}), (b {id: 'SXVI-T-84799090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8480'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-84801000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-84802000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-848030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848030'}), (b {id: 'SXVI-T-84803010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848030'}), (b {id: 'SXVI-T-84803090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-84804100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-84804900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-84805000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-84806000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-848071'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848071'}), (b {id: 'SXVI-T-84807110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848071'}), (b {id: 'SXVI-T-84807190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8480'}), (b {id: 'SXVI-T-848079'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848079'}), (b {id: 'SXVI-T-84807910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848079'}), (b {id: 'SXVI-T-84807990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8481'}), (b {id: 'SXVI-T-848110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848110'}), (b {id: 'SXVI-T-84811011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848110'}), (b {id: 'SXVI-T-84811019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848110'}), (b {id: 'SXVI-T-84811021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848110'}), (b {id: 'SXVI-T-84811022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848110'}), (b {id: 'SXVI-T-84811091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848110'}), (b {id: 'SXVI-T-84811099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8481'}), (b {id: 'SXVI-T-848120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848120'}), (b {id: 'SXVI-T-84812011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848120'}), (b {id: 'SXVI-T-84812019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848120'}), (b {id: 'SXVI-T-84812020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848120'}), (b {id: 'SXVI-T-84812090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8481'}), (b {id: 'SXVI-T-848130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848130'}), (b {id: 'SXVI-T-84813010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848130'}), (b {id: 'SXVI-T-84813020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848130'}), (b {id: 'SXVI-T-84813040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848130'}), (b {id: 'SXVI-T-84813090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8481'}), (b {id: 'SXVI-T-848140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848140'}), (b {id: 'SXVI-T-84814010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848140'}), (b {id: 'SXVI-T-84814030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848140'}), (b {id: 'SXVI-T-84814090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8481'}), (b {id: 'SXVI-T-848180'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818014'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818061'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818062'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818063'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818064'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818065'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818066'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818067'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818071'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818072'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818073'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818074'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818077'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818078'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818079'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818081'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818082'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818083'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818084'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818096'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818097'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818098'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848180'}), (b {id: 'SXVI-T-84818099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8481'}), (b {id: 'SXVI-T-848190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819023'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848190'}), (b {id: 'SXVI-T-84819090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8482'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84821000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84822000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84823000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84824000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84825000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84828000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84829100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8482'}), (b {id: 'SXVI-T-84829900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8483'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8483'}), (b {id: 'SXVI-T-848310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831024'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831025'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831026'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831027'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848310'}), (b {id: 'SXVI-T-84831090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8483'}), (b {id: 'SXVI-T-848320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848320'}), (b {id: 'SXVI-T-84832020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848320'}), (b {id: 'SXVI-T-84832030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848320'}), (b {id: 'SXVI-T-84832090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8483'}), (b {id: 'SXVI-T-848330'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848330'}), (b {id: 'SXVI-T-84833030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848330'}), (b {id: 'SXVI-T-84833090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8483'}), (b {id: 'SXVI-T-848340'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848340'}), (b {id: 'SXVI-T-84834020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848340'}), (b {id: 'SXVI-T-84834030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848340'}), (b {id: 'SXVI-T-84834040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848340'}), (b {id: 'SXVI-T-84834090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8483'}), (b {id: 'SXVI-T-84835000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8483'}), (b {id: 'SXVI-T-84836000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8483'}), (b {id: 'SXVI-T-848390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839014'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839015'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848390'}), (b {id: 'SXVI-T-84839099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8484'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8484'}), (b {id: 'SXVI-T-84841000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8484'}), (b {id: 'SXVI-T-84842000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8484'}), (b {id: 'SXVI-T-84849000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8485'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8485'}), (b {id: 'SXVI-T-84851000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8485'}), (b {id: 'SXVI-T-84852000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8485'}), (b {id: 'SXVI-T-848530'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848530'}), (b {id: 'SXVI-T-84853010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848530'}), (b {id: 'SXVI-T-84853090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8485'}), (b {id: 'SXVI-T-84858000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8485'}), (b {id: 'SXVI-T-848590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848590'}), (b {id: 'SXVI-T-84859010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848590'}), (b {id: 'SXVI-T-84859090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8486'}), (b {id: 'SXVI-T-848610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848610'}), (b {id: 'SXVI-T-84861010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848610'}), (b {id: 'SXVI-T-84861020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848610'}), (b {id: 'SXVI-T-84861030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848610'}), (b {id: 'SXVI-T-84861040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848610'}), (b {id: 'SXVI-T-84861050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848610'}), (b {id: 'SXVI-T-84861060'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848610'}), (b {id: 'SXVI-T-84861090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8486'}), (b {id: 'SXVI-T-848620'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862033'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862042'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848620'}), (b {id: 'SXVI-T-84862099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8486'}), (b {id: 'SXVI-T-848630'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848630'}), (b {id: 'SXVI-T-84863010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848630'}), (b {id: 'SXVI-T-84863020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848630'}), (b {id: 'SXVI-T-84863030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848630'}), (b {id: 'SXVI-T-84863090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8486'}), (b {id: 'SXVI-T-848640'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864060'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864070'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848640'}), (b {id: 'SXVI-T-84864090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8486'}), (b {id: 'SXVI-T-848690'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869014'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869015'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869016'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869017'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869023'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869024'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869025'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869026'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869027'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869028'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869033'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869034'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869035'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869036'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869042'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869043'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869044'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869045'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869046'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-848690'}), (b {id: 'SXVI-T-84869049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-84'}), (b {id: 'SXVI-T-8487'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8487'}), (b {id: 'SXVI-T-84871000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8487'}), (b {id: 'SXVI-T-84879000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011060'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850110'}), (b {id: 'SXVI-T-85011099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850120'}), (b {id: 'SXVI-T-85012012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850120'}), (b {id: 'SXVI-T-85012019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850120'}), (b {id: 'SXVI-T-85012021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850120'}), (b {id: 'SXVI-T-85012029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850131'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850131'}), (b {id: 'SXVI-T-85013130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850131'}), (b {id: 'SXVI-T-85013160'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850131'}), (b {id: 'SXVI-T-85013170'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850131'}), (b {id: 'SXVI-T-85013180'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850132'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850132'}), (b {id: 'SXVI-T-85013221'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850132'}), (b {id: 'SXVI-T-85013224'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850132'}), (b {id: 'SXVI-T-85013225'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850132'}), (b {id: 'SXVI-T-85013226'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850132'}), (b {id: 'SXVI-T-85013231'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850132'}), (b {id: 'SXVI-T-85013232'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850132'}), (b {id: 'SXVI-T-85013233'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850133'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850133'}), (b {id: 'SXVI-T-85013310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850133'}), (b {id: 'SXVI-T-85013390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-85013400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850140'}), (b {id: 'SXVI-T-85014011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850140'}), (b {id: 'SXVI-T-85014019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850140'}), (b {id: 'SXVI-T-85014021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850140'}), (b {id: 'SXVI-T-85014029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850151'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850151'}), (b {id: 'SXVI-T-85015111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850151'}), (b {id: 'SXVI-T-85015119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850152'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015212'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015221'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015222'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015229'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015231'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015232'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850152'}), (b {id: 'SXVI-T-85015239'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850153'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850153'}), (b {id: 'SXVI-T-85015310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850153'}), (b {id: 'SXVI-T-85015390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850161'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850161'}), (b {id: 'SXVI-T-85016110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850161'}), (b {id: 'SXVI-T-85016120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850162'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850162'}), (b {id: 'SXVI-T-85016210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850162'}), (b {id: 'SXVI-T-85016220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-85016300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-85016400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-85017100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850172'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850172'}), (b {id: 'SXVI-T-85017210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850172'}), (b {id: 'SXVI-T-85017220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850172'}), (b {id: 'SXVI-T-85017230'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850172'}), (b {id: 'SXVI-T-85017240'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8501'}), (b {id: 'SXVI-T-850180'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850180'}), (b {id: 'SXVI-T-85018010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850180'}), (b {id: 'SXVI-T-85018020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850180'}), (b {id: 'SXVI-T-85018030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850180'}), (b {id: 'SXVI-T-85018040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8502'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8502'}), (b {id: 'SXVI-T-85021100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8502'}), (b {id: 'SXVI-T-850212'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850212'}), (b {id: 'SXVI-T-85021210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850212'}), (b {id: 'SXVI-T-85021220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8502'}), (b {id: 'SXVI-T-850213'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850213'}), (b {id: 'SXVI-T-85021320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850213'}), (b {id: 'SXVI-T-85021390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8502'}), (b {id: 'SXVI-T-850220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850220'}), (b {id: 'SXVI-T-85022010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850220'}), (b {id: 'SXVI-T-85022020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850220'}), (b {id: 'SXVI-T-85022030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850220'}), (b {id: 'SXVI-T-85022042'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850220'}), (b {id: 'SXVI-T-85022049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8502'}), (b {id: 'SXVI-T-850231'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850231'}), (b {id: 'SXVI-T-85023110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850231'}), (b {id: 'SXVI-T-85023120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8502'}), (b {id: 'SXVI-T-850239'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850239'}), (b {id: 'SXVI-T-85023910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850239'}), (b {id: 'SXVI-T-85023920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850239'}), (b {id: 'SXVI-T-85023932'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850239'}), (b {id: 'SXVI-T-85023939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8502'}), (b {id: 'SXVI-T-85024000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8503'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8503'}), (b {id: 'SXVI-T-85030020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8503'}), (b {id: 'SXVI-T-85030090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-85041000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850421'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850421'}), (b {id: 'SXVI-T-85042111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850421'}), (b {id: 'SXVI-T-85042119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850421'}), (b {id: 'SXVI-T-85042192'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850421'}), (b {id: 'SXVI-T-85042193'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850421'}), (b {id: 'SXVI-T-85042199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850422'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850422'}), (b {id: 'SXVI-T-85042211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850422'}), (b {id: 'SXVI-T-85042219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850422'}), (b {id: 'SXVI-T-85042292'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850422'}), (b {id: 'SXVI-T-85042293'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850422'}), (b {id: 'SXVI-T-85042299'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850423'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850423'}), (b {id: 'SXVI-T-85042310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850423'}), (b {id: 'SXVI-T-85042321'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850423'}), (b {id: 'SXVI-T-85042322'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850423'}), (b {id: 'SXVI-T-85042329'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850431'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043112'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043113'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043121'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043122'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043123'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043124'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043129'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043192'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043193'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850431'}), (b {id: 'SXVI-T-85043199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850432'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043230'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043241'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043249'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043251'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850432'}), (b {id: 'SXVI-T-85043259'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850433'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850433'}), (b {id: 'SXVI-T-85043311'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850433'}), (b {id: 'SXVI-T-85043319'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850433'}), (b {id: 'SXVI-T-85043391'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850433'}), (b {id: 'SXVI-T-85043399'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850434'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043411'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043412'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043413'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043414'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043415'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043419'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043422'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043423'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043424'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043425'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043426'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850434'}), (b {id: 'SXVI-T-85043429'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850440'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850440'}), (b {id: 'SXVI-T-85044011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850440'}), (b {id: 'SXVI-T-85044019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850440'}), (b {id: 'SXVI-T-85044020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850440'}), (b {id: 'SXVI-T-85044030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850440'}), (b {id: 'SXVI-T-85044040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850440'}), (b {id: 'SXVI-T-85044090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850450'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850450'}), (b {id: 'SXVI-T-85045010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850450'}), (b {id: 'SXVI-T-85045020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850450'}), (b {id: 'SXVI-T-85045093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850450'}), (b {id: 'SXVI-T-85045094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850450'}), (b {id: 'SXVI-T-85045095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8504'}), (b {id: 'SXVI-T-850490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850490'}), (b {id: 'SXVI-T-85049010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850490'}), (b {id: 'SXVI-T-85049020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850490'}), (b {id: 'SXVI-T-85049031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850490'}), (b {id: 'SXVI-T-85049039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850490'}), (b {id: 'SXVI-T-85049041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850490'}), (b {id: 'SXVI-T-85049049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850490'}), (b {id: 'SXVI-T-85049090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8505'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8505'}), (b {id: 'SXVI-T-85051100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8505'}), (b {id: 'SXVI-T-85051900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8505'}), (b {id: 'SXVI-T-85052000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8505'}), (b {id: 'SXVI-T-850590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850590'}), (b {id: 'SXVI-T-85059010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850590'}), (b {id: 'SXVI-T-85059020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850590'}), (b {id: 'SXVI-T-85059090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8506'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8506'}), (b {id: 'SXVI-T-850610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850610'}), (b {id: 'SXVI-T-85061011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850610'}), (b {id: 'SXVI-T-85061012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850610'}), (b {id: 'SXVI-T-85061019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850610'}), (b {id: 'SXVI-T-85061091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850610'}), (b {id: 'SXVI-T-85061099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8506'}), (b {id: 'SXVI-T-85063000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8506'}), (b {id: 'SXVI-T-85064000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8506'}), (b {id: 'SXVI-T-85065000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8506'}), (b {id: 'SXVI-T-850660'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850660'}), (b {id: 'SXVI-T-85066010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850660'}), (b {id: 'SXVI-T-85066090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8506'}), (b {id: 'SXVI-T-850680'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850680'}), (b {id: 'SXVI-T-85068030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850680'}), (b {id: 'SXVI-T-85068090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8506'}), (b {id: 'SXVI-T-85069000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8507'}), (b {id: 'SXVI-T-850710'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850710'}), (b {id: 'SXVI-T-85071010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850710'}), (b {id: 'SXVI-T-85071092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850710'}), (b {id: 'SXVI-T-85071095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850710'}), (b {id: 'SXVI-T-85071096'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850710'}), (b {id: 'SXVI-T-85071097'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850710'}), (b {id: 'SXVI-T-85071098'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850710'}), (b {id: 'SXVI-T-85071099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8507'}), (b {id: 'SXVI-T-850720'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850720'}), (b {id: 'SXVI-T-85072010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850720'}), (b {id: 'SXVI-T-85072094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850720'}), (b {id: 'SXVI-T-85072095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850720'}), (b {id: 'SXVI-T-85072096'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850720'}), (b {id: 'SXVI-T-85072097'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850720'}), (b {id: 'SXVI-T-85072098'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850720'}), (b {id: 'SXVI-T-85072099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8507'}), (b {id: 'SXVI-T-850730'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850730'}), (b {id: 'SXVI-T-85073010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850730'}), (b {id: 'SXVI-T-85073090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8507'}), (b {id: 'SXVI-T-850750'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850750'}), (b {id: 'SXVI-T-85075010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850750'}), (b {id: 'SXVI-T-85075020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850750'}), (b {id: 'SXVI-T-85075090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8507'}), (b {id: 'SXVI-T-850760'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850760'}), (b {id: 'SXVI-T-85076031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850760'}), (b {id: 'SXVI-T-85076032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850760'}), (b {id: 'SXVI-T-85076033'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850760'}), (b {id: 'SXVI-T-85076039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850760'}), (b {id: 'SXVI-T-85076090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8507'}), (b {id: 'SXVI-T-850780'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850780'}), (b {id: 'SXVI-T-85078011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850780'}), (b {id: 'SXVI-T-85078019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850780'}), (b {id: 'SXVI-T-85078020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850780'}), (b {id: 'SXVI-T-85078091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850780'}), (b {id: 'SXVI-T-85078099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8507'}), (b {id: 'SXVI-T-850790'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850790'}), (b {id: 'SXVI-T-85079011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850790'}), (b {id: 'SXVI-T-85079012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850790'}), (b {id: 'SXVI-T-85079019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850790'}), (b {id: 'SXVI-T-85079091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850790'}), (b {id: 'SXVI-T-85079092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850790'}), (b {id: 'SXVI-T-85079093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850790'}), (b {id: 'SXVI-T-85079099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8508'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8508'}), (b {id: 'SXVI-T-85081100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8508'}), (b {id: 'SXVI-T-850819'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850819'}), (b {id: 'SXVI-T-85081910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850819'}), (b {id: 'SXVI-T-85081990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8508'}), (b {id: 'SXVI-T-85086000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8508'}), (b {id: 'SXVI-T-850870'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850870'}), (b {id: 'SXVI-T-85087010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850870'}), (b {id: 'SXVI-T-85087090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8509'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8509'}), (b {id: 'SXVI-T-85094000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8509'}), (b {id: 'SXVI-T-850980'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850980'}), (b {id: 'SXVI-T-85098010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850980'}), (b {id: 'SXVI-T-85098020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850980'}), (b {id: 'SXVI-T-85098090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8509'}), (b {id: 'SXVI-T-850990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850990'}), (b {id: 'SXVI-T-85099010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-850990'}), (b {id: 'SXVI-T-85099090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8510'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8510'}), (b {id: 'SXVI-T-85101000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8510'}), (b {id: 'SXVI-T-85102000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8510'}), (b {id: 'SXVI-T-85103000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8510'}), (b {id: 'SXVI-T-85109000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8511'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8511'}), (b {id: 'SXVI-T-851110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851110'}), (b {id: 'SXVI-T-85111010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851110'}), (b {id: 'SXVI-T-85111020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851110'}), (b {id: 'SXVI-T-85111090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8511'}), (b {id: 'SXVI-T-851120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851120'}), (b {id: 'SXVI-T-85112010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851120'}), (b {id: 'SXVI-T-85112021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851120'}), (b {id: 'SXVI-T-85112029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851120'}), (b {id: 'SXVI-T-85112091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851120'}), (b {id: 'SXVI-T-85112099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8511'}), (b {id: 'SXVI-T-851130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851130'}), (b {id: 'SXVI-T-85113030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851130'}), (b {id: 'SXVI-T-85113041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851130'}), (b {id: 'SXVI-T-85113049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851130'}), (b {id: 'SXVI-T-85113091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851130'}), (b {id: 'SXVI-T-85113099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8511'}), (b {id: 'SXVI-T-851140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114033'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851140'}), (b {id: 'SXVI-T-85114099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8511'}), (b {id: 'SXVI-T-851150'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115033'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851150'}), (b {id: 'SXVI-T-85115099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8511'}), (b {id: 'SXVI-T-851180'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851180'}), (b {id: 'SXVI-T-85118010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851180'}), (b {id: 'SXVI-T-85118020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851180'}), (b {id: 'SXVI-T-85118090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8511'}), (b {id: 'SXVI-T-851190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851190'}), (b {id: 'SXVI-T-85119010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851190'}), (b {id: 'SXVI-T-85119020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851190'}), (b {id: 'SXVI-T-85119090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8512'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8512'}), (b {id: 'SXVI-T-85121000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8512'}), (b {id: 'SXVI-T-851220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851220'}), (b {id: 'SXVI-T-85122020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851220'}), (b {id: 'SXVI-T-85122091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851220'}), (b {id: 'SXVI-T-85122099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8512'}), (b {id: 'SXVI-T-851230'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851230'}), (b {id: 'SXVI-T-85123010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851230'}), (b {id: 'SXVI-T-85123020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851230'}), (b {id: 'SXVI-T-85123091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851230'}), (b {id: 'SXVI-T-85123099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8512'}), (b {id: 'SXVI-T-85124000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8512'}), (b {id: 'SXVI-T-851290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851290'}), (b {id: 'SXVI-T-85129010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851290'}), (b {id: 'SXVI-T-85129020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8513'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8513'}), (b {id: 'SXVI-T-851310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851310'}), (b {id: 'SXVI-T-85131030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851310'}), (b {id: 'SXVI-T-85131090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8513'}), (b {id: 'SXVI-T-851390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851390'}), (b {id: 'SXVI-T-85139010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851390'}), (b {id: 'SXVI-T-85139030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851390'}), (b {id: 'SXVI-T-85139090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8514'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-85141100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-85141900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-851420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851420'}), (b {id: 'SXVI-T-85142020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851420'}), (b {id: 'SXVI-T-85142090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-851431'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851431'}), (b {id: 'SXVI-T-85143110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851431'}), (b {id: 'SXVI-T-85143190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-851432'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851432'}), (b {id: 'SXVI-T-85143210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851432'}), (b {id: 'SXVI-T-85143290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-851439'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851439'}), (b {id: 'SXVI-T-85143910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851439'}), (b {id: 'SXVI-T-85143990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-85144000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8514'}), (b {id: 'SXVI-T-851490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851490'}), (b {id: 'SXVI-T-85149020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851490'}), (b {id: 'SXVI-T-85149090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8515'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-85151100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-851519'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851519'}), (b {id: 'SXVI-T-85151911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851519'}), (b {id: 'SXVI-T-85151919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851519'}), (b {id: 'SXVI-T-85151990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-85152100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-85152900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-85153100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-851539'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851539'}), (b {id: 'SXVI-T-85153910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851539'}), (b {id: 'SXVI-T-85153990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-851580'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851580'}), (b {id: 'SXVI-T-85158010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851580'}), (b {id: 'SXVI-T-85158090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8515'}), (b {id: 'SXVI-T-851590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851590'}), (b {id: 'SXVI-T-85159010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851590'}), (b {id: 'SXVI-T-85159021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851590'}), (b {id: 'SXVI-T-85159029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851590'}), (b {id: 'SXVI-T-85159090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8516'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-851610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851610'}), (b {id: 'SXVI-T-85161011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851610'}), (b {id: 'SXVI-T-85161019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851610'}), (b {id: 'SXVI-T-85161030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85162100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85162900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85163100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85163200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85163300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-851640'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851640'}), (b {id: 'SXVI-T-85164010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851640'}), (b {id: 'SXVI-T-85164090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85165000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-851660'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851660'}), (b {id: 'SXVI-T-85166010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851660'}), (b {id: 'SXVI-T-85166090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85167100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-85167200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-851679'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851679'}), (b {id: 'SXVI-T-85167910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851679'}), (b {id: 'SXVI-T-85167990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-851680'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851680'}), (b {id: 'SXVI-T-85168010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851680'}), (b {id: 'SXVI-T-85168030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851680'}), (b {id: 'SXVI-T-85168090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8516'}), (b {id: 'SXVI-T-851690'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851690'}), (b {id: 'SXVI-T-85169021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851690'}), (b {id: 'SXVI-T-85169029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851690'}), (b {id: 'SXVI-T-85169030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851690'}), (b {id: 'SXVI-T-85169040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851690'}), (b {id: 'SXVI-T-85169090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8517'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-85171100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-85171300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-85171400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-85171800'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-85176100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-851762'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176230'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176241'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176242'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176243'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176249'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176251'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176252'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176253'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176259'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176261'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176269'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176291'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176292'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851762'}), (b {id: 'SXVI-T-85176299'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-85176900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-85177100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8517'}), (b {id: 'SXVI-T-851779'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177931'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177932'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177992'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851779'}), (b {id: 'SXVI-T-85177999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8518'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851810'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851810'}), (b {id: 'SXVI-T-85181011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851810'}), (b {id: 'SXVI-T-85181019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851810'}), (b {id: 'SXVI-T-85181090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851821'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851821'}), (b {id: 'SXVI-T-85182110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851821'}), (b {id: 'SXVI-T-85182190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851822'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851822'}), (b {id: 'SXVI-T-85182210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851822'}), (b {id: 'SXVI-T-85182290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851829'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851829'}), (b {id: 'SXVI-T-85182920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851829'}), (b {id: 'SXVI-T-85182990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851830'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851830'}), (b {id: 'SXVI-T-85183010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851830'}), (b {id: 'SXVI-T-85183020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851830'}), (b {id: 'SXVI-T-85183040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851830'}), (b {id: 'SXVI-T-85183051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851830'}), (b {id: 'SXVI-T-85183059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851830'}), (b {id: 'SXVI-T-85183090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851840'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851840'}), (b {id: 'SXVI-T-85184020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851840'}), (b {id: 'SXVI-T-85184030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851840'}), (b {id: 'SXVI-T-85184040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851840'}), (b {id: 'SXVI-T-85184090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851850'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851850'}), (b {id: 'SXVI-T-85185010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851850'}), (b {id: 'SXVI-T-85185020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851850'}), (b {id: 'SXVI-T-85185090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8518'}), (b {id: 'SXVI-T-851890'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851890'}), (b {id: 'SXVI-T-85189010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851890'}), (b {id: 'SXVI-T-85189020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851890'}), (b {id: 'SXVI-T-85189030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851890'}), (b {id: 'SXVI-T-85189040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851890'}), (b {id: 'SXVI-T-85189090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8519'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8519'}), (b {id: 'SXVI-T-851920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851920'}), (b {id: 'SXVI-T-85192010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851920'}), (b {id: 'SXVI-T-85192090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8519'}), (b {id: 'SXVI-T-85193000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8519'}), (b {id: 'SXVI-T-851981'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198141'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198149'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198150'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198161'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198162'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198169'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198171'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198179'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851981'}), (b {id: 'SXVI-T-85198199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8519'}), (b {id: 'SXVI-T-851989'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851989'}), (b {id: 'SXVI-T-85198910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851989'}), (b {id: 'SXVI-T-85198920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851989'}), (b {id: 'SXVI-T-85198930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851989'}), (b {id: 'SXVI-T-85198940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-851989'}), (b {id: 'SXVI-T-85198990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8521'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8521'}), (b {id: 'SXVI-T-852110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852110'}), (b {id: 'SXVI-T-85211010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852110'}), (b {id: 'SXVI-T-85211090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8521'}), (b {id: 'SXVI-T-852190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852190'}), (b {id: 'SXVI-T-85219011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852190'}), (b {id: 'SXVI-T-85219019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852190'}), (b {id: 'SXVI-T-85219091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852190'}), (b {id: 'SXVI-T-85219099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8522'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8522'}), (b {id: 'SXVI-T-85221000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8522'}), (b {id: 'SXVI-T-852290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852290'}), (b {id: 'SXVI-T-85229099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-852321'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852321'}), (b {id: 'SXVI-T-85232110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852321'}), (b {id: 'SXVI-T-85232190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232931'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232933'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232941'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232942'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232943'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232949'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232951'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232952'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232959'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232961'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232962'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232963'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232969'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232971'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232979'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232981'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232982'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232983'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232985'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232986'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232989'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232992'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232993'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232994'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232995'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852329'}), (b {id: 'SXVI-T-85232999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-852341'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852341'}), (b {id: 'SXVI-T-85234110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852341'}), (b {id: 'SXVI-T-85234190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-852349'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234912'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234913'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234914'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234915'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234916'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234992'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234993'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852349'}), (b {id: 'SXVI-T-85234999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-852351'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235121'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235129'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235192'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852351'}), (b {id: 'SXVI-T-85235199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-85235200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-852359'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852359'}), (b {id: 'SXVI-T-85235910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852359'}), (b {id: 'SXVI-T-85235921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852359'}), (b {id: 'SXVI-T-85235929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852359'}), (b {id: 'SXVI-T-85235930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852359'}), (b {id: 'SXVI-T-85235940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852359'}), (b {id: 'SXVI-T-85235990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8523'}), (b {id: 'SXVI-T-852380'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852380'}), (b {id: 'SXVI-T-85238040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852380'}), (b {id: 'SXVI-T-85238051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852380'}), (b {id: 'SXVI-T-85238059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852380'}), (b {id: 'SXVI-T-85238091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852380'}), (b {id: 'SXVI-T-85238092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852380'}), (b {id: 'SXVI-T-85238099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8524'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8524'}), (b {id: 'SXVI-T-85241100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8524'}), (b {id: 'SXVI-T-85241200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8524'}), (b {id: 'SXVI-T-85241900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8524'}), (b {id: 'SXVI-T-85249100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8524'}), (b {id: 'SXVI-T-85249200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8524'}), (b {id: 'SXVI-T-85249900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8525'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8525'}), (b {id: 'SXVI-T-85255000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8525'}), (b {id: 'SXVI-T-85256000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8525'}), (b {id: 'SXVI-T-852581'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852581'}), (b {id: 'SXVI-N-CH85_SUBNOTE_1'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852581'}), (b {id: 'SXVI-T-85258110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852581'}), (b {id: 'SXVI-T-85258120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852581'}), (b {id: 'SXVI-T-85258190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8525'}), (b {id: 'SXVI-T-852582'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852582'}), (b {id: 'SXVI-N-CH85_SUBNOTE_2'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852582'}), (b {id: 'SXVI-T-85258210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852582'}), (b {id: 'SXVI-T-85258220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852582'}), (b {id: 'SXVI-T-85258290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8525'}), (b {id: 'SXVI-T-852583'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852583'}), (b {id: 'SXVI-N-CH85_SUBNOTE_3'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852583'}), (b {id: 'SXVI-T-85258310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852583'}), (b {id: 'SXVI-T-85258320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852583'}), (b {id: 'SXVI-T-85258390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8525'}), (b {id: 'SXVI-T-852589'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852589'}), (b {id: 'SXVI-T-85258910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852589'}), (b {id: 'SXVI-T-85258920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852589'}), (b {id: 'SXVI-T-85258930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852589'}), (b {id: 'SXVI-T-85258990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8526'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8526'}), (b {id: 'SXVI-T-852610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852610'}), (b {id: 'SXVI-T-85261010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852610'}), (b {id: 'SXVI-T-85261090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8526'}), (b {id: 'SXVI-T-852691'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852691'}), (b {id: 'SXVI-T-85269110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852691'}), (b {id: 'SXVI-T-85269190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8526'}), (b {id: 'SXVI-T-85269200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8527'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-85271200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85271200'}), (b {id: 'SXVI-N-CH85_SUBNOTE_4'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-852713'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852713'}), (b {id: 'SXVI-T-85271310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852713'}), (b {id: 'SXVI-T-85271390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-852719'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852719'}), (b {id: 'SXVI-T-85271920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852719'}), (b {id: 'SXVI-T-85271990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-852721'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852721'}), (b {id: 'SXVI-T-85272110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852721'}), (b {id: 'SXVI-T-85272190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-85272900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-852791'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852791'}), (b {id: 'SXVI-T-85279110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852791'}), (b {id: 'SXVI-T-85279190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-852792'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852792'}), (b {id: 'SXVI-T-85279220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852792'}), (b {id: 'SXVI-T-85279290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8527'}), (b {id: 'SXVI-T-852799'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852799'}), (b {id: 'SXVI-T-85279920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852799'}), (b {id: 'SXVI-T-85279990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8528'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-85284200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-852849'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852849'}), (b {id: 'SXVI-T-85284910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852849'}), (b {id: 'SXVI-T-85284920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-85285200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-852859'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852859'}), (b {id: 'SXVI-T-85285910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852859'}), (b {id: 'SXVI-T-85285920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-85286200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-852869'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852869'}), (b {id: 'SXVI-T-85286910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852869'}), (b {id: 'SXVI-T-85286990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-852871'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852871'}), (b {id: 'SXVI-T-85287111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852871'}), (b {id: 'SXVI-T-85287119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852871'}), (b {id: 'SXVI-T-85287191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852871'}), (b {id: 'SXVI-T-85287199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-852872'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852872'}), (b {id: 'SXVI-T-85287210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852872'}), (b {id: 'SXVI-T-85287291'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852872'}), (b {id: 'SXVI-T-85287292'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852872'}), (b {id: 'SXVI-T-85287299'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8528'}), (b {id: 'SXVI-T-85287300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8529'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8529'}), (b {id: 'SXVI-T-852910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291060'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852910'}), (b {id: 'SXVI-T-85291099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8529'}), (b {id: 'SXVI-T-852990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299052'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299053'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299054'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299055'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-852990'}), (b {id: 'SXVI-T-85299099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8530'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8530'}), (b {id: 'SXVI-T-85301000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8530'}), (b {id: 'SXVI-T-85308000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8530'}), (b {id: 'SXVI-T-85309000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8531'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8531'}), (b {id: 'SXVI-T-853110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853110'}), (b {id: 'SXVI-T-85311010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853110'}), (b {id: 'SXVI-T-85311020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853110'}), (b {id: 'SXVI-T-85311030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853110'}), (b {id: 'SXVI-T-85311090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8531'}), (b {id: 'SXVI-T-85312000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8531'}), (b {id: 'SXVI-T-853180'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853180'}), (b {id: 'SXVI-T-85318011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853180'}), (b {id: 'SXVI-T-85318019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853180'}), (b {id: 'SXVI-T-85318021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853180'}), (b {id: 'SXVI-T-85318029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853180'}), (b {id: 'SXVI-T-85318090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8531'}), (b {id: 'SXVI-T-853190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853190'}), (b {id: 'SXVI-T-85319010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853190'}), (b {id: 'SXVI-T-85319020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853190'}), (b {id: 'SXVI-T-85319030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853190'}), (b {id: 'SXVI-T-85319090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8532'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85321000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85322100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85322200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85322300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85322400'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85322500'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85322900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85323000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8532'}), (b {id: 'SXVI-T-85329000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8533'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8533'}), (b {id: 'SXVI-T-853310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853310'}), (b {id: 'SXVI-T-85331010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853310'}), (b {id: 'SXVI-T-85331090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8533'}), (b {id: 'SXVI-T-85332100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8533'}), (b {id: 'SXVI-T-85332900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8533'}), (b {id: 'SXVI-T-85333100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8533'}), (b {id: 'SXVI-T-85333900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8533'}), (b {id: 'SXVI-T-85334000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8533'}), (b {id: 'SXVI-T-85339000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8534'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8534'}), (b {id: 'SXVI-N-CH85_NOTE_8'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8534'}), (b {id: 'SXVI-T-85340010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85340010'}), (b {id: 'SXVI-N-CH85_NOTE_8'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8534'}), (b {id: 'SXVI-T-85340020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85340020'}), (b {id: 'SXVI-N-CH85_NOTE_8'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8534'}), (b {id: 'SXVI-T-85340030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85340030'}), (b {id: 'SXVI-N-CH85_NOTE_8'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8534'}), (b {id: 'SXVI-T-85340090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85340090'}), (b {id: 'SXVI-N-CH85_NOTE_8'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8535'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8535'}), (b {id: 'SXVI-T-85351000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8535'}), (b {id: 'SXVI-T-853521'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853521'}), (b {id: 'SXVI-T-85352110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853521'}), (b {id: 'SXVI-T-85352120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853521'}), (b {id: 'SXVI-T-85352190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8535'}), (b {id: 'SXVI-T-853529'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853529'}), (b {id: 'SXVI-T-85352910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853529'}), (b {id: 'SXVI-T-85352990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8535'}), (b {id: 'SXVI-T-853530'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853530'}), (b {id: 'SXVI-T-85353011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853530'}), (b {id: 'SXVI-T-85353019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853530'}), (b {id: 'SXVI-T-85353020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853530'}), (b {id: 'SXVI-T-85353090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8535'}), (b {id: 'SXVI-T-85354000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8535'}), (b {id: 'SXVI-T-853590'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853590'}), (b {id: 'SXVI-T-85359010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853590'}), (b {id: 'SXVI-T-85359020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853590'}), (b {id: 'SXVI-T-85359090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8536'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853610'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361011'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361012'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361013'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361019'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361091'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361092'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361093'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853610'}), (b {id: 'SXVI-T-85361099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85361099'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853620'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-T-85362011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85362011'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-T-85362012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85362012'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-T-85362013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85362013'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-T-85362019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85362019'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-T-85362020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85362020'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-T-85362091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85362091'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853620'}), (b {id: 'SXVI-T-85362099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85362099'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853630'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853630'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853630'}), (b {id: 'SXVI-T-85363010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85363010'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853630'}), (b {id: 'SXVI-T-85363020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85363020'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853630'}), (b {id: 'SXVI-T-85363090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85363090'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853641'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853641'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853641'}), (b {id: 'SXVI-T-85364110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364110'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853641'}), (b {id: 'SXVI-T-85364120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364120'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853641'}), (b {id: 'SXVI-T-85364130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364130'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853641'}), (b {id: 'SXVI-T-85364140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364140'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853641'}), (b {id: 'SXVI-T-85364191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364191'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853641'}), (b {id: 'SXVI-T-85364199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364199'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853649'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853649'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853649'}), (b {id: 'SXVI-T-85364910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364910'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853649'}), (b {id: 'SXVI-T-85364990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85364990'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853650'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365020'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365032'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365033'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365033'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365039'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365040'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365051'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365051'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365059'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365059'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365061'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365061'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365069'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365069'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365095'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365095'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365096'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365096'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853650'}), (b {id: 'SXVI-T-85365099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85365099'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853661'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853661'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853661'}), (b {id: 'SXVI-T-85366111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366111'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853661'}), (b {id: 'SXVI-T-85366119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366119'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853661'}), (b {id: 'SXVI-T-85366191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366191'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853661'}), (b {id: 'SXVI-T-85366199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366199'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853669'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366910'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366923'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366923'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366924'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366924'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366929'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366932'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366932'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366939'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366992'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366992'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853669'}), (b {id: 'SXVI-T-85366999'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85366999'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853670'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853670'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853670'}), (b {id: 'SXVI-T-85367010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85367010'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853670'}), (b {id: 'SXVI-T-85367020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85367020'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853670'}), (b {id: 'SXVI-T-85367090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85367090'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8536'}), (b {id: 'SXVI-T-853690'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369012'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369019'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369022'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369029'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369032'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369032'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369039'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369040'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369093'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369093'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369094'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369094'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853690'}), (b {id: 'SXVI-T-85369099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85369099'}), (b {id: 'SXVI-N-CH85_NOTE_9'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8537'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8537'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8537'}), (b {id: 'SXVI-T-853710'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371011'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371012'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371013'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371019'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371020'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371030'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371040'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371091'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371092'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371092'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853710'}), (b {id: 'SXVI-T-85371099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85371099'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8537'}), (b {id: 'SXVI-T-853720'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853720'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853720'}), (b {id: 'SXVI-T-85372011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85372011'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853720'}), (b {id: 'SXVI-T-85372019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85372019'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853720'}), (b {id: 'SXVI-T-85372021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85372021'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853720'}), (b {id: 'SXVI-T-85372029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85372029'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853720'}), (b {id: 'SXVI-T-85372090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85372090'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8538'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8538'}), (b {id: 'SXVI-T-853810'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853810'}), (b {id: 'SXVI-T-85381011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853810'}), (b {id: 'SXVI-T-85381012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853810'}), (b {id: 'SXVI-T-85381019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853810'}), (b {id: 'SXVI-T-85381021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853810'}), (b {id: 'SXVI-T-85381022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853810'}), (b {id: 'SXVI-T-85381029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8538'}), (b {id: 'SXVI-T-853890'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853890'}), (b {id: 'SXVI-T-85389011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853890'}), (b {id: 'SXVI-T-85389012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853890'}), (b {id: 'SXVI-T-85389013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853890'}), (b {id: 'SXVI-T-85389019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853890'}), (b {id: 'SXVI-T-85389020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853910'}), (b {id: 'SXVI-T-85391010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853910'}), (b {id: 'SXVI-T-85391090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853921'}), (b {id: 'SXVI-T-85392120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853921'}), (b {id: 'SXVI-T-85392130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853921'}), (b {id: 'SXVI-T-85392140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853921'}), (b {id: 'SXVI-T-85392190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853922'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392231'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392232'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392233'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392239'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392291'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392293'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853922'}), (b {id: 'SXVI-T-85392299'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392930'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392941'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392949'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392950'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392960'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853929'}), (b {id: 'SXVI-T-85392990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853931'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853931'}), (b {id: 'SXVI-T-85393110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853931'}), (b {id: 'SXVI-T-85393120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853931'}), (b {id: 'SXVI-T-85393130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853931'}), (b {id: 'SXVI-T-85393190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-85393200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853939'}), (b {id: 'SXVI-T-85393910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853939'}), (b {id: 'SXVI-T-85393920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853939'}), (b {id: 'SXVI-T-85393940'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853939'}), (b {id: 'SXVI-T-85393990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-85394100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-85394900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-85395100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85395100'}), (b {id: 'SXVI-N-CH85_NOTE_11A'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853952'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853952'}), (b {id: 'SXVI-N-CH85_NOTE_11B'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853952'}), (b {id: 'SXVI-T-85395210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85395210'}), (b {id: 'SXVI-N-CH85_NOTE_11B'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853952'}), (b {id: 'SXVI-T-85395290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85395290'}), (b {id: 'SXVI-N-CH85_NOTE_11B'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8539'}), (b {id: 'SXVI-T-853990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853990'}), (b {id: 'SXVI-T-85399010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853990'}), (b {id: 'SXVI-T-85399020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853990'}), (b {id: 'SXVI-T-85399030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-853990'}), (b {id: 'SXVI-T-85399090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8540'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85401100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85401200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85402000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-854040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854040'}), (b {id: 'SXVI-T-85404010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854040'}), (b {id: 'SXVI-T-85404090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85406000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85407100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85407900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85408100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85408900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85409100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8540'}), (b {id: 'SXVI-T-85409900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-N-CH85_NOTE_12A_II'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85411000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85411000'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85411000'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85412100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85412100'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85412100'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85412900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85412900'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85412900'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85413000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85413000'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85413000'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85414100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414100'}), (b {id: 'SXVI-N-CH85_NOTE_12A_II'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414100'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85414200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414200'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414200'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85414300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414300'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414300'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85414900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414900'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85414900'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85415100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85415100'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85415100'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_TRANSDUCER'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85415100'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85415900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85415900'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85415900'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85416000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85416000'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85416000'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8541'}), (b {id: 'SXVI-T-85419000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85419000'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85419000'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8542'}), (b {id: 'SXVI-N-CH85_NOTE_12B_INTRO'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8542'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8542'}), (b {id: 'SXVI-T-85423100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423100'}), (b {id: 'SXVI-N-CH85_NOTE_12B_INTRO'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423100'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8542'}), (b {id: 'SXVI-T-85423200'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423200'}), (b {id: 'SXVI-N-CH85_NOTE_12B_INTRO'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423200'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8542'}), (b {id: 'SXVI-T-85423300'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423300'}), (b {id: 'SXVI-N-CH85_NOTE_12B_INTRO'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423300'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8542'}), (b {id: 'SXVI-T-85423900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423900'}), (b {id: 'SXVI-N-CH85_NOTE_12B_INTRO'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85423900'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8542'}), (b {id: 'SXVI-T-85429000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85429000'}), (b {id: 'SXVI-N-CH85_NOTE_12B_INTRO'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85429000'}), (b {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8543'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8543'}), (b {id: 'SXVI-T-85431000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8543'}), (b {id: 'SXVI-T-85432000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8543'}), (b {id: 'SXVI-T-854330'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854330'}), (b {id: 'SXVI-T-85433020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854330'}), (b {id: 'SXVI-T-85433091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854330'}), (b {id: 'SXVI-T-85433099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8543'}), (b {id: 'SXVI-T-85434000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8543'}), (b {id: 'SXVI-T-854370'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85437021'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85437029'}), (b {id: 'SXVI-N-CH85_NOTE_10'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437050'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437060'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854370'}), (b {id: 'SXVI-T-85437090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8543'}), (b {id: 'SXVI-T-854390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854390'}), (b {id: 'SXVI-T-85439010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854390'}), (b {id: 'SXVI-T-85439020'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854390'}), (b {id: 'SXVI-T-85439030'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854390'}), (b {id: 'SXVI-T-85439040'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854390'}), (b {id: 'SXVI-T-85439090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8544'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-854411'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854411'}), (b {id: 'SXVI-T-85441120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854411'}), (b {id: 'SXVI-T-85441130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854411'}), (b {id: 'SXVI-T-85441140'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854411'}), (b {id: 'SXVI-T-85441190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-85441900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-854420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442041'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854420'}), (b {id: 'SXVI-T-85442049'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-854430'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854430'}), (b {id: 'SXVI-T-85443012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854430'}), (b {id: 'SXVI-T-85443013'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854430'}), (b {id: 'SXVI-T-85443014'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854430'}), (b {id: 'SXVI-T-85443019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854430'}), (b {id: 'SXVI-T-85443091'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854430'}), (b {id: 'SXVI-T-85443099'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444211'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444213'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444219'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444221'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444223'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444229'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444232'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444233'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444234'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444239'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444291'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444292'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444294'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444295'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444296'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444297'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854442'}), (b {id: 'SXVI-T-85444299'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-854449'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444913'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444921'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444922'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444923'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444924'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444929'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444931'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444932'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444933'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444939'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444941'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444942'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854449'}), (b {id: 'SXVI-T-85444949'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-854460'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446011'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446012'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446019'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446021'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446022'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446029'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446031'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854460'}), (b {id: 'SXVI-T-85446039'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8544'}), (b {id: 'SXVI-T-854470'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854470'}), (b {id: 'SXVI-T-85447010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854470'}), (b {id: 'SXVI-T-85447090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8545'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8545'}), (b {id: 'SXVI-T-85451100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8545'}), (b {id: 'SXVI-T-85451900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8545'}), (b {id: 'SXVI-T-85452000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8545'}), (b {id: 'SXVI-T-85459000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8546'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8546'}), (b {id: 'SXVI-T-85461000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8546'}), (b {id: 'SXVI-T-854620'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854620'}), (b {id: 'SXVI-T-85462010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854620'}), (b {id: 'SXVI-T-85462090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8546'}), (b {id: 'SXVI-T-85469000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8547'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8547'}), (b {id: 'SXVI-T-85471000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8547'}), (b {id: 'SXVI-T-85472000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8547'}), (b {id: 'SXVI-T-854790'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854790'}), (b {id: 'SXVI-T-85479010'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854790'}), (b {id: 'SXVI-T-85479090'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8548'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8548'}), (b {id: 'SXVI-T-85480000'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-CH-85'}), (b {id: 'SXVI-T-8549'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-854911'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491111'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491111'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491112'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491112'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491119'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491119'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491120'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491120'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491130'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491130'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491191'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491191'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491192'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491192'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854911'}), (b {id: 'SXVI-T-85491199'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491199'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-854912'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854912'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854912'}), (b {id: 'SXVI-T-85491210'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491210'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854912'}), (b {id: 'SXVI-T-85491220'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491220'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854912'}), (b {id: 'SXVI-T-85491290'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491290'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-854913'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854913'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854913'}), (b {id: 'SXVI-T-85491310'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491310'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854913'}), (b {id: 'SXVI-T-85491320'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491320'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854913'}), (b {id: 'SXVI-T-85491390'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491390'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-854914'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854914'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854914'}), (b {id: 'SXVI-T-85491410'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491410'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854914'}), (b {id: 'SXVI-T-85491420'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491420'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854914'}), (b {id: 'SXVI-T-85491490'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491490'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-854919'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854919'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854919'}), (b {id: 'SXVI-T-85491910'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491910'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854919'}), (b {id: 'SXVI-T-85491920'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491920'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854919'}), (b {id: 'SXVI-T-85491990'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-85491990'}), (b {id: 'SXVI-N-CH85_SUBNOTE_5'})
                    CREATE (a)-[:CONSTRAINED_BY]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-85492100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-85492900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-85493100'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-85493900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-854991'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854991'}), (b {id: 'SXVI-T-85499110'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-854991'}), (b {id: 'SXVI-T-85499190'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-T-8549'}), (b {id: 'SXVI-T-85499900'})
                    CREATE (a)-[:CONTAINS]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1_INTRO'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1A'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1B'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1C'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1D'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1E'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1F'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1F'}), (b {id: 'SXVI-T-8522'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1G'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1H'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1IJ'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1K'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1L'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1M'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1N'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1O'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1P'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_1Q'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2_INTRO'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2_INTRO'}), (b {id: 'SXVI-T-8484'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2_INTRO'}), (b {id: 'SXVI-T-8544'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2_INTRO'}), (b {id: 'SXVI-T-8545'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2_INTRO'}), (b {id: 'SXVI-T-8546'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2_INTRO'}), (b {id: 'SXVI-T-8547'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8466'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8473'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8487'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8503'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8522'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8529'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8538'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2A'}), (b {id: 'SXVI-T-8548'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8479'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8543'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8466'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8473'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8503'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8522'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8529'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8538'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8517'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8525'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8526'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8527'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8528'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2B'}), (b {id: 'SXVI-T-8524'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8466'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8473'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8503'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8522'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8529'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8538'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8487'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_2C'}), (b {id: 'SXVI-T-8548'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_3'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_4'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_5'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_6A_INTRO'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_6A_INTRO'}), (b {id: 'SXVI-T-8549'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_6A_I'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_6A_II'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_6B'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_6B'}), (b {id: 'SXVI-T-8549'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-SXVI_NOTE_6C'}), (b {id: 'SXVI-S-XVI'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1_INTRO'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1A'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1B'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1C'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1D'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1E'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1E'}), (b {id: 'SXVI-T-8508'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1F'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1F'}), (b {id: 'SXVI-T-8509'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1F'}), (b {id: 'SXVI-T-8525'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1G'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_1H'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2_MAIN'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2_MAIN'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2A'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2A'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2A'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2A'}), (b {id: 'SXVI-T-8437'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2A'}), (b {id: 'SXVI-T-8438'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2A'}), (b {id: 'SXVI-T-8451'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2B'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2B'}), (b {id: 'SXVI-T-8422'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2B'}), (b {id: 'SXVI-T-8452'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2B'}), (b {id: 'SXVI-T-8472'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2C'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2C'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2C'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_2C'}), (b {id: 'SXVI-T-8456'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8456'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8457'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8458'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8459'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8460'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8461'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8464'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_3'}), (b {id: 'SXVI-T-8465'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_4'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_4'}), (b {id: 'SXVI-T-8457'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_5'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_5'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6A'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6A'}), (b {id: 'SXVI-T-8471'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6B'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6B'}), (b {id: 'SXVI-T-8471'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6C'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6C'}), (b {id: 'SXVI-T-8471'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6D'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6D'}), (b {id: 'SXVI-T-8471'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6E'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_6E'}), (b {id: 'SXVI-T-8471'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_7'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_7'}), (b {id: 'SXVI-T-8482'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_8'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_8'}), (b {id: 'SXVI-T-8479'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_9'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_9'}), (b {id: 'SXVI-T-8470'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_10'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_10'}), (b {id: 'SXVI-T-8485'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11B'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11B'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11C'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11C'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11D'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11D'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_SUBNOTE_1'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_SUBNOTE_2'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_SUBNOTE_2'}), (b {id: 'SXVI-T-847149'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_SUBNOTE_3'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_SUBNOTE_3'}), (b {id: 'SXVI-T-848120'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_SUBNOTE_3'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_SUBNOTE_4'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_1_INTRO'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_1A'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_1B'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_1C'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_1C'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_1D'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_1E'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_2'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_2'}), (b {id: 'SXVI-T-8511'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_2'}), (b {id: 'SXVI-T-8512'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_2'}), (b {id: 'SXVI-T-8540'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_2'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_2'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_2'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_3'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_3'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_INTRO'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_INTRO'}), (b {id: 'SXVI-T-8509'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4A'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4A'}), (b {id: 'SXVI-T-8509'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4B'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4B'}), (b {id: 'SXVI-T-8509'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8509'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8422'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8450'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8420'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8451'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8452'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8467'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_4_EXCLUSION'}), (b {id: 'SXVI-T-8516'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_5'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_5'}), (b {id: 'SXVI-T-8517'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_6_INTRO'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_6_INTRO'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_6A'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_6A'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_6B'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_6B'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_7'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_7'}), (b {id: 'SXVI-T-8524'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_8'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_8'}), (b {id: 'SXVI-T-8534'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_8'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_9'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_9'}), (b {id: 'SXVI-T-8536'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_10'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_10'}), (b {id: 'SXVI-T-8537'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_10'}), (b {id: 'SXVI-T-8543'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11_INTRO'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11_INTRO'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11A'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11A'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11A'}), (b {id: 'SXVI-T-8536'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11A'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11B'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_11B'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12_INTRO'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12_INTRO'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12_INTRO'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_TRANSDUCER'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_TRANSDUCER'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_TRANSDUCER'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_DEF1'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_DEF2'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_DEF3'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_DEF4'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_DEF5'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_I_DEF6'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_II'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12A_II'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_INTRO'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_INTRO'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_I'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_II'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_III'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV'}), (b {id: 'SXVI-T-8532'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV'}), (b {id: 'SXVI-T-8533'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF1'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF2'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3A'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3B'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3C'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3D'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_NOTE_12_PRIORITY'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_1'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_1'}), (b {id: 'SXVI-T-852581'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_2'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_2'}), (b {id: 'SXVI-T-852582'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_3'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_3'}), (b {id: 'SXVI-T-852583'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_3'}), (b {id: 'SXVI-T-852589'})
                    CREATE (a)-[:REFERENCES_CODE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_4'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH85_SUBNOTE_5'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:APPLIES_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0001'}), (b {id: 'SXVI-T-8402'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0002'}), (b {id: 'SXVI-T-8402'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0003'}), (b {id: 'SXVI-T-8402'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0004'}), (b {id: 'SXVI-T-8402'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0005'}), (b {id: 'SXVI-T-8402'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0006'}), (b {id: 'SXVI-T-8404'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0007'}), (b {id: 'SXVI-T-8404'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0008'}), (b {id: 'SXVI-T-8406'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0009'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0010'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0011'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0012'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0013'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0014'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0015'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0016'}), (b {id: 'SXVI-T-8407'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0017'}), (b {id: 'SXVI-T-8408'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0018'}), (b {id: 'SXVI-T-8408'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0019'}), (b {id: 'SXVI-T-8408'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0020'}), (b {id: 'SXVI-T-8408'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0021'}), (b {id: 'SXVI-T-8408'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0022'}), (b {id: 'SXVI-T-8408'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0023'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0024'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0025'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0026'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0027'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0028'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0029'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0030'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0031'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0032'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0033'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0034'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0035'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0036'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0037'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0038'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0039'}), (b {id: 'SXVI-T-8409'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0040'}), (b {id: 'SXVI-T-8410'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0041'}), (b {id: 'SXVI-T-8411'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0042'}), (b {id: 'SXVI-T-8411'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0043'}), (b {id: 'SXVI-T-8411'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0044'}), (b {id: 'SXVI-T-8411'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0045'}), (b {id: 'SXVI-T-8412'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0046'}), (b {id: 'SXVI-T-8412'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0047'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0048'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0049'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0050'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0051'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0052'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0053'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0054'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0055'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0056'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0057'}), (b {id: 'SXVI-T-8413'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0058'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0059'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0060'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0061'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0062'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0063'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0064'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0065'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0066'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0067'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0068'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0069'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0070'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0071'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0072'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0073'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0074'}), (b {id: 'SXVI-T-8414'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0075'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0076'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0077'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0078'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0079'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0080'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0081'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0082'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0083'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0084'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0085'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0086'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0087'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0088'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0089'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0090'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0091'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0092'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0093'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0094'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0095'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0096'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0097'}), (b {id: 'SXVI-T-8415'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0098'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0099'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0100'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0101'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0102'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0103'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0104'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0105'}), (b {id: 'SXVI-T-8418'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0106'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0107'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0108'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0109'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0110'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0111'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX_0112'}), (b {id: 'SXVI-T-8419'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0001'}), (b {id: 'SXVI-T-8420'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0002'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0003'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0004'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0005'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0006'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0007'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0008'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0009'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0010'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0011'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0012'}), (b {id: 'SXVI-T-8421'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0013'}), (b {id: 'SXVI-T-8422'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0014'}), (b {id: 'SXVI-T-8423'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0015'}), (b {id: 'SXVI-T-8423'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0016'}), (b {id: 'SXVI-T-8423'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0017'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0018'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0019'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0020'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0021'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0022'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0023'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0024'}), (b {id: 'SXVI-T-8424'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0025'}), (b {id: 'SXVI-T-8425'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0026'}), (b {id: 'SXVI-T-8425'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0027'}), (b {id: 'SXVI-T-8425'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0028'}), (b {id: 'SXVI-T-8426'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0029'}), (b {id: 'SXVI-T-8426'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0030'}), (b {id: 'SXVI-T-8426'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0031'}), (b {id: 'SXVI-T-8428'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0032'}), (b {id: 'SXVI-T-8428'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0033'}), (b {id: 'SXVI-T-8429'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0034'}), (b {id: 'SXVI-T-8429'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0035'}), (b {id: 'SXVI-T-8430'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0036'}), (b {id: 'SXVI-T-8430'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0037'}), (b {id: 'SXVI-T-8430'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0038'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0039'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0040'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0041'}), (b {id: 'SXVI-T-8431'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0042'}), (b {id: 'SXVI-T-8432'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0043'}), (b {id: 'SXVI-T-8432'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0044'}), (b {id: 'SXVI-T-8432'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0045'}), (b {id: 'SXVI-T-8433'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0046'}), (b {id: 'SXVI-T-8433'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0047'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0048'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0049'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0050'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0051'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0052'}), (b {id: 'SXVI-T-8436'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0053'}), (b {id: 'SXVI-T-8437'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0054'}), (b {id: 'SXVI-T-8437'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0055'}), (b {id: 'SXVI-T-8437'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0056'}), (b {id: 'SXVI-T-8437'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0057'}), (b {id: 'SXVI-T-8438'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0058'}), (b {id: 'SXVI-T-8438'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0059'}), (b {id: 'SXVI-T-8438'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0060'}), (b {id: 'SXVI-T-8438'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0061'}), (b {id: 'SXVI-T-8438'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX4_0062'}), (b {id: 'SXVI-T-8439'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0001'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0002'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0003'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0004'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0005'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0006'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0007'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0008'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0009'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0010'}), (b {id: 'SXVI-T-8443'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0011'}), (b {id: 'SXVI-T-8445'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0012'}), (b {id: 'SXVI-T-8446'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0013'}), (b {id: 'SXVI-T-8447'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0014'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0015'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0016'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0017'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0018'}), (b {id: 'SXVI-T-8448'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0019'}), (b {id: 'SXVI-T-8450'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0020'}), (b {id: 'SXVI-T-8450'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0021'}), (b {id: 'SXVI-T-8450'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0022'}), (b {id: 'SXVI-T-8451'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0023'}), (b {id: 'SXVI-T-8452'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0024'}), (b {id: 'SXVI-T-8452'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0025'}), (b {id: 'SXVI-T-8452'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0026'}), (b {id: 'SXVI-T-8455'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0027'}), (b {id: 'SXVI-T-8456'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0028'}), (b {id: 'SXVI-T-8458'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0029'}), (b {id: 'SXVI-T-8458'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0030'}), (b {id: 'SXVI-T-8459'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0031'}), (b {id: 'SXVI-T-8459'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0032'}), (b {id: 'SXVI-T-8459'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0033'}), (b {id: 'SXVI-T-8459'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX5_0034'}), (b {id: 'SXVI-T-8459'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0001'}), (b {id: 'SXVI-T-8460'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0002'}), (b {id: 'SXVI-T-8460'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0003'}), (b {id: 'SXVI-T-8460'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0004'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0005'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0006'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0007'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0008'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0009'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0010'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0011'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0012'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0013'}), (b {id: 'SXVI-T-8462'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0014'}), (b {id: 'SXVI-T-8465'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0015'}), (b {id: 'SXVI-T-8466'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0016'}), (b {id: 'SXVI-T-8467'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0017'}), (b {id: 'SXVI-T-8467'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0018'}), (b {id: 'SXVI-T-8467'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX6_0019'}), (b {id: 'SXVI-T-8467'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0001'}), (b {id: 'SXVI-T-8470'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0002'}), (b {id: 'SXVI-T-8471'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0003'}), (b {id: 'SXVI-T-8472'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0004'}), (b {id: 'SXVI-T-8473'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0005'}), (b {id: 'SXVI-T-8474'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0006'}), (b {id: 'SXVI-T-8474'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0007'}), (b {id: 'SXVI-T-8474'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0008'}), (b {id: 'SXVI-T-8474'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0009'}), (b {id: 'SXVI-T-8474'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0010'}), (b {id: 'SXVI-T-8475'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0011'}), (b {id: 'SXVI-T-8476'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0012'}), (b {id: 'SXVI-T-8476'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0013'}), (b {id: 'SXVI-T-8477'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0014'}), (b {id: 'SXVI-T-8477'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0015'}), (b {id: 'SXVI-T-8477'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0016'}), (b {id: 'SXVI-T-8477'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0017'}), (b {id: 'SXVI-T-8479'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0018'}), (b {id: 'SXVI-T-8479'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX7_0019'}), (b {id: 'SXVI-T-8479'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0001'}), (b {id: 'SXVI-T-8480'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0002'}), (b {id: 'SXVI-T-8480'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0003'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0004'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0005'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0006'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0007'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0008'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0009'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0010'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0011'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0012'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0013'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0014'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0015'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0016'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0017'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0018'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0019'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0020'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0021'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0022'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0023'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0024'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0025'}), (b {id: 'SXVI-T-8481'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0026'}), (b {id: 'SXVI-T-8482'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0027'}), (b {id: 'SXVI-T-8483'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0028'}), (b {id: 'SXVI-T-8483'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0029'}), (b {id: 'SXVI-T-8483'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0030'}), (b {id: 'SXVI-T-8483'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0031'}), (b {id: 'SXVI-T-8483'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0032'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0033'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0034'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0035'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0036'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0037'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0038'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0039'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0040'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0041'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0042'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0043'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0044'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX8_0045'}), (b {id: 'SXVI-T-8486'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0001'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0002'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0003'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0004'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0005'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0006'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0007'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0008'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0009'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0010'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0011'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0012'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0013'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0014'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0015'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0016'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0017'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0018'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0019'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0020'}), (b {id: 'SXVI-T-8501'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0021'}), (b {id: 'SXVI-T-8502'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0022'}), (b {id: 'SXVI-T-8502'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0023'}), (b {id: 'SXVI-T-8502'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0024'}), (b {id: 'SXVI-T-8502'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0025'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0026'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0027'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0028'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0029'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0030'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0031'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0032'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0033'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0034'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0035'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0036'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0037'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0038'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0039'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0040'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0041'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0042'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0043'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0044'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0045'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0046'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0047'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0048'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0049'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0050'}), (b {id: 'SXVI-T-8504'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0051'}), (b {id: 'SXVI-T-8505'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0052'}), (b {id: 'SXVI-T-8506'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0053'}), (b {id: 'SXVI-T-8506'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0054'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0055'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0056'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0057'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0058'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0059'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0060'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0061'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0062'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0063'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0064'}), (b {id: 'SXVI-T-8507'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CTX10_0065'}), (b {id: 'SXVI-T-8508'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_001'}), (b {id: 'SXVI-T-851120'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_002'}), (b {id: 'SXVI-T-851120'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_003'}), (b {id: 'SXVI-T-851130'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_004'}), (b {id: 'SXVI-T-851130'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_005'}), (b {id: 'SXVI-T-851140'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_006'}), (b {id: 'SXVI-T-851140'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_007'}), (b {id: 'SXVI-T-851140'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_008'}), (b {id: 'SXVI-T-851150'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_009'}), (b {id: 'SXVI-T-851150'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_010'}), (b {id: 'SXVI-T-851150'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_011'}), (b {id: 'SXVI-T-851230'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_012'}), (b {id: 'SXVI-T-8514'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_013'}), (b {id: 'SXVI-T-8514'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_014'}), (b {id: 'SXVI-T-8515'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_015'}), (b {id: 'SXVI-T-8515'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_016'}), (b {id: 'SXVI-T-8515'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_017'}), (b {id: 'SXVI-T-851610'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_018'}), (b {id: 'SXVI-T-8516'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_019'}), (b {id: 'SXVI-T-8516'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_020'}), (b {id: 'SXVI-T-8516'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_021'}), (b {id: 'SXVI-T-851690'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_022'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_023'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_024'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_025'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_026'}), (b {id: 'SXVI-CH-85'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P11_CTX_027'}), (b {id: 'SXVI-T-851590'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_001'}), (b {id: 'SXVI-T-8517'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_002'}), (b {id: 'SXVI-T-8517'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_003'}), (b {id: 'SXVI-T-851762'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_004'}), (b {id: 'SXVI-T-851762'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_005'}), (b {id: 'SXVI-T-851762'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_006'}), (b {id: 'SXVI-T-851762'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_007'}), (b {id: 'SXVI-T-8517'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_008'}), (b {id: 'SXVI-T-851779'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_009'}), (b {id: 'SXVI-T-851779'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_010'}), (b {id: 'SXVI-T-851779'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_011'}), (b {id: 'SXVI-T-851810'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_012'}), (b {id: 'SXVI-T-8518'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P12_CTX_013'}), (b {id: 'SXVI-T-851830'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_001'}), (b {id: 'SXVI-T-8519'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_002'}), (b {id: 'SXVI-T-851981'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_003'}), (b {id: 'SXVI-T-851981'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_004'}), (b {id: 'SXVI-T-851981'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_005'}), (b {id: 'SXVI-T-851981'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_006'}), (b {id: 'SXVI-T-852190'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_007'}), (b {id: 'SXVI-T-852190'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_008'}), (b {id: 'SXVI-T-852290'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_009'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_010'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_011'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_012'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_013'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_014'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_015'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_016'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_017'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_018'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_019'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_020'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_021'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_022'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_023'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_024'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_025'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_026'}), (b {id: 'SXVI-T-852329'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_027'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_028'}), (b {id: 'SXVI-T-852349'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_029'}), (b {id: 'SXVI-T-852349'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_030'}), (b {id: 'SXVI-T-852349'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_031'}), (b {id: 'SXVI-T-8523'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_032'}), (b {id: 'SXVI-T-852351'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_033'}), (b {id: 'SXVI-T-852351'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_034'}), (b {id: 'SXVI-T-852351'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_035'}), (b {id: 'SXVI-T-852351'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_036'}), (b {id: 'SXVI-T-852359'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_037'}), (b {id: 'SXVI-T-852359'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_038'}), (b {id: 'SXVI-T-852380'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_039'}), (b {id: 'SXVI-T-852380'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_040'}), (b {id: 'SXVI-T-8524'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P13_CTX_041'}), (b {id: 'SXVI-T-8524'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_001'}), (b {id: 'SXVI-T-8525'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_002'}), (b {id: 'SXVI-T-8526'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_003'}), (b {id: 'SXVI-T-8527'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_004'}), (b {id: 'SXVI-T-8527'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_005'}), (b {id: 'SXVI-T-8527'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_006'}), (b {id: 'SXVI-T-8528'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_007'}), (b {id: 'SXVI-T-8528'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_008'}), (b {id: 'SXVI-T-8528'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_009'}), (b {id: 'SXVI-T-8528'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_010'}), (b {id: 'SXVI-T-852871'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_011'}), (b {id: 'SXVI-T-852871'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_012'}), (b {id: 'SXVI-T-852872'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_013'}), (b {id: 'SXVI-T-852910'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_014'}), (b {id: 'SXVI-T-852910'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_015'}), (b {id: 'SXVI-T-852990'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_016'}), (b {id: 'SXVI-T-852990'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P14_CTX_017'}), (b {id: 'SXVI-T-852990'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_001'}), (b {id: 'SXVI-T-853180'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_002'}), (b {id: 'SXVI-T-853180'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_003'}), (b {id: 'SXVI-T-8532'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_004'}), (b {id: 'SXVI-T-8533'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_005'}), (b {id: 'SXVI-T-8533'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_006'}), (b {id: 'SXVI-T-8535'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_007'}), (b {id: 'SXVI-T-853530'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_008'}), (b {id: 'SXVI-T-853610'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_009'}), (b {id: 'SXVI-T-853610'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_010'}), (b {id: 'SXVI-T-853620'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_011'}), (b {id: 'SXVI-T-853620'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_012'}), (b {id: 'SXVI-T-8536'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_013'}), (b {id: 'SXVI-T-853641'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_014'}), (b {id: 'SXVI-T-853650'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_015'}), (b {id: 'SXVI-T-853650'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_016'}), (b {id: 'SXVI-T-853650'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_017'}), (b {id: 'SXVI-T-853650'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_018'}), (b {id: 'SXVI-T-8536'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_019'}), (b {id: 'SXVI-T-853661'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_020'}), (b {id: 'SXVI-T-853661'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_021'}), (b {id: 'SXVI-T-853669'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_022'}), (b {id: 'SXVI-T-853669'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_023'}), (b {id: 'SXVI-T-853669'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_024'}), (b {id: 'SXVI-T-853690'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_025'}), (b {id: 'SXVI-T-853690'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_026'}), (b {id: 'SXVI-T-853690'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_027'}), (b {id: 'SXVI-T-853690'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_028'}), (b {id: 'SXVI-T-853690'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_029'}), (b {id: 'SXVI-T-853710'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_030'}), (b {id: 'SXVI-T-853710'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_031'}), (b {id: 'SXVI-T-853720'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_032'}), (b {id: 'SXVI-T-853720'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_033'}), (b {id: 'SXVI-T-853810'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_034'}), (b {id: 'SXVI-T-853810'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_035'}), (b {id: 'SXVI-T-853890'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_036'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_037'}), (b {id: 'SXVI-T-853922'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_038'}), (b {id: 'SXVI-T-853922'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_039'}), (b {id: 'SXVI-T-853929'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_040'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_041'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P15_CTX_042'}), (b {id: 'SXVI-T-8539'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_001'}), (b {id: 'SXVI-T-8540'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_002'}), (b {id: 'SXVI-T-8540'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_003'}), (b {id: 'SXVI-T-8540'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_004'}), (b {id: 'SXVI-T-8540'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_005'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_006'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_007'}), (b {id: 'SXVI-T-8541'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_008'}), (b {id: 'SXVI-T-8542'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_009'}), (b {id: 'SXVI-T-854330'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_010'}), (b {id: 'SXVI-T-854370'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_011'}), (b {id: 'SXVI-T-8544'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_012'}), (b {id: 'SXVI-T-854420'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_013'}), (b {id: 'SXVI-T-854420'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_014'}), (b {id: 'SXVI-T-854420'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_015'}), (b {id: 'SXVI-T-854420'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_016'}), (b {id: 'SXVI-T-854430'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_017'}), (b {id: 'SXVI-T-854430'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_018'}), (b {id: 'SXVI-T-854430'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_019'}), (b {id: 'SXVI-T-854430'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_020'}), (b {id: 'SXVI-T-8544'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_021'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_022'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_023'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_024'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_025'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_026'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_027'}), (b {id: 'SXVI-T-854449'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_028'}), (b {id: 'SXVI-T-854449'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_029'}), (b {id: 'SXVI-T-854449'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_030'}), (b {id: 'SXVI-T-854449'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_031'}), (b {id: 'SXVI-T-854449'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_032'}), (b {id: 'SXVI-T-854460'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_033'}), (b {id: 'SXVI-T-854460'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_034'}), (b {id: 'SXVI-T-854460'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_035'}), (b {id: 'SXVI-T-8545'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_036'}), (b {id: 'SXVI-T-8549'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_037'}), (b {id: 'SXVI-T-854911'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_038'}), (b {id: 'SXVI-T-854911'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_039'}), (b {id: 'SXVI-T-8549'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_040'}), (b {id: 'SXVI-T-8549'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-C-CH85_P16_CTX_041'}), (b {id: 'SXVI-T-8549'})
                    CREATE (a)-[:CONTEXT_WITHIN]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH84_FOOTNOTE_1A'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:ANNOTATES_SCOPE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH84_FOOTNOTE_1B'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:ANNOTATES_SCOPE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH84_FOOTNOTE_SEN'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:ANNOTATES_SCOPE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH84_FOOTNOTE_STAR'}), (b {id: 'SXVI-CH-84'})
                    CREATE (a)-[:ANNOTATES_SCOPE]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P13_FOOTNOTE_85235910'}), (b {id: 'SXVI-T-85235910'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P16_FOOTNOTE_TCVN_7697_2'}), (b {id: 'SXVI-T-85433020'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P16_FOOTNOTE_TCVN_7697_2'}), (b {id: 'SXVI-T-85437040'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P16_FOOTNOTE_SEN'}), (b {id: 'SXVI-T-85437050'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P16_FOOTNOTE_8544_CONDUCTORS'}), (b {id: 'SXVI-T-8544'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P16_FOOTNOTE_8544_CONDUCTORS'}), (b {id: 'SXVI-T-854442'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P16_FOOTNOTE_8544_CONDUCTORS'}), (b {id: 'SXVI-T-854449'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-F-CH85_P16_FOOTNOTE_8544_CONDUCTORS'}), (b {id: 'SXVI-T-854460'})
                    CREATE (a)-[:ANNOTATES]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_TRANSDUCER'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_DEF1'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_DEF2'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_DEF3'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_DEF4'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_DEF5'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_I_DEF6'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12A_II'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_INTRO'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_I'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_II'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_III'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_IV'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF1'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF2'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3A'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3B'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3C'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
SELECT * FROM cypher('customs_tariff_graph', $$
                    MATCH (a {id: 'SXVI-N-CH84_NOTE_11A'}), (b {id: 'SXVI-N-CH85_NOTE_12B_IV_DEF3D'})
                    CREATE (a)-[:NORMALIZED_REFERENCE_TO]->(b)
                $$) as (e agtype);
