-- Industry-Mappings mit robusten Regex-Mustern
INSERT INTO domain_rule (rule_type, rule_key, rule_value) VALUES
                                                              ('INDUSTRY_MAPPING', 'IT & Software', '(?i).*(IT|Software|Entwicklung|Cloud|Informatik).*'),
                                                              ('INDUSTRY_MAPPING', 'Finanzen', '(?i).*(Finanz|Bank|Versicherung|Aktie|Bilanz).*'),
                                                              ('INDUSTRY_MAPPING', 'Automobil', '(?i).*(Automobil|Maschinenbau|Fertigung|Anlage).*'),
                                                              ('INDUSTRY_MAPPING', 'Gesundheit', '(?i).*(Klinik|Pflege|Therapie|Krankenhaus).*'),
                                                              ('INDUSTRY_MAPPING', 'Logistik', '(?i).*(Handel|Logistik|Einzelhandel|Lager|Supply Chain).*')
ON CONFLICT (rule_type, rule_key) DO NOTHING;
