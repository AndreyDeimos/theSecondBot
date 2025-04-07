SELECT u.first_name, c.name
FROM users u
JOIN registrations r ON u.chat_id = r.chat_id
JOIN competitions c ON r.competition_id = c.id 
 
