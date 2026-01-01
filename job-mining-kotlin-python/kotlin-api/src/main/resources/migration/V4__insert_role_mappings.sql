-- Befüllen der Rollen-Mappings
INSERT INTO domain_rule (rule_type, rule_key, rule_value) VALUES
                                                              ('ROLE_MAPPING', 'Software Engineer', '(?i).*(software|entwickler|developer|programmer).*'),
                                                              ('ROLE_MAPPING', 'Data Scientist', '(?i).*(data scientist|data analyst|machine learning).*'),
                                                              ('ROLE_MAPPING', 'Project Manager', '(?i).*(project manager|projektleiter|product owner).*'),
                                                              ('ROLE_MAPPING', 'Consultant', '(?i).*(consultant|berater).*'),
                                                              ('ROLE_MAPPING', 'Architect', '(?i).*(architect|architekt).*')
    ON CONFLICT (rule_type, rule_key) DO NOTHING;
