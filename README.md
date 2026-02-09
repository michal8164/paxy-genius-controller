parcel_dimensions.csv:

SELECT cust.username, p.tracking_nr, pd.ordering, pd.price, p.carrier_id, pd.dimension_id, pd.free_dimension_id, p.type, p.free_transport, p.charge, pd.weight FROM parcel_dimension pd LEFT JOIN parcel p ON pd.parcel_id=p.id LEFT JOIN registerBook b ON p.book_id=b.id LEFT JOIN customer cust ON b.customer_id=cust.id WHERE p.send_date >= '2026-01-01' AND p.send_date <= '2026-01-31' AND p.emag_id IS NOT NULL

emag_clubs_01.csv from server
no_genius from server