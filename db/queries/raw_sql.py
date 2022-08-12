banks_request_sql = """
SELECT DISTINCT id,
                mass_address,
                rezident,
                rnp,
                bankrupt
FROM banks as main_data
LEFT JOIN (
    SELECT array_agg(bg_type_id) as bg_types,
           bank_id
    FROM bank_bg_types
    GROUP BY bank_id
) as bank_bg on bank_bg.bank_id = main_data.id
LEFT JOIN (
    SELECT array_agg(fz_type_id) as fz_types,
           bank_id
    FROM bank_fz_types
    GROUP BY bank_id
) as bank_fz on bank_fz.bank_id = main_data.id
LEFT JOIN (
    SELECT array_agg(company_type_id) as company_types,
           bank_id
    FROM bank_company_types
    GROUP BY bank_id
) as bank_company_type on bank_company_type.bank_id = main_data.id
WHERE min_days <= {request_days} AND max_days >= {request_days}
AND min_guarante <= {request_amount} AND max_guarante >= {request_amount}
AND min_company_dates <= {request_company_days} AND authorized_capital <= {request_capital}
AND ({request_last_revenue} * (percent_revenue / 100)) <= {request_amount}
AND lesion_quarterly_amount <= {request_lession_quarterly}
AND execution_lists_amount <= {request_execution_amount}
AND amount_debt_on_taxes_and_fees <= {request_debt_amount}
AND {request_bg_type} = ANY(bg_types)
AND {request_fz_type} = ANY(fz_types)
AND {request_company_type} = ANY(company_types)
"""

request_info_sql = """
SELECT id,
       inn,
       purchase_number,
       amount,
       days,
       json_agg(json_build_object('bank_id', bank_id, 'bank_name', bank_name, 'bank_stavka', bank_stavka,
       'brokers_terms', brokers_terms)) as banks
FROM bg_request as main_data
         LEFT JOIN (SELECT bank as bank_id,
                           request
                    FROM bg_request_banks
                    WHERE request = {request_id}) as bank_id on bank_id.request = main_data.id
         LEFT JOIN (SELECT name   as bank_name,
                           id     as bank_info_id,
                           manager_id,
                           stavka as bank_stavka,
                           brokers_terms
                    FROM banks) as bank_info on bank_info.bank_info_id = bank_id.bank_id
WHERE id = {request_id}
GROUP BY id
"""
