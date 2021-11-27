-- almost the whole db
  select m.id, m.model, m.version, a.id, u.first_fetch, u.last_fetch, u.description, u.price
    from maker_model m
    join ad a on a.model_id = m.id
    join ad_update u on a.id = u.ad_id
order by m.model, m.version, a.id
;

-- prices by model
  select m.model, count(a.id), min(u.price), avg(u.price), max(u.price)
    from maker_model m
    join ad a on a.model_id = m.id
    join ad_update u on a.id = u.ad_id
group by m.model
order by m.model
;
