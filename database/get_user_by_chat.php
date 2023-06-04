<?php
require 'database.php';

$id = $_GET['id'];

if (!is_numeric($id)) {
    echo json_encode(["message" => "Важно передовать только число"]);
    die();
}

$query = <<<EOT
    SELECT 
        `user`.`id`,
        `telegram_chat_id`,
        `text`,
        `status`.`name` AS 'status',
        `telegram_name`,
        `age`,
        `city`,
        `user`.`name`
    FROM `user` 
    JOIN `status` ON `user`.`status_id` = `status`.`id`
    WHERE `user`.`telegram_chat_id` = '${id}' LIMIT 1
EOT;

$db = new DataBase();
$db->connect();


$users = [];
$row = $db->query_answer($query);
$user = $row[0];


if (count($row) == 0) {
    http_response_code(404);
    echo json_encode(["message" => "Пользователь с Telegram-чатом ${name} не найден"]);
    die();
}

$query = "SELECT `word`FROM `key_word` WHERE `user_id` = ${user['id']}";
$words = [];
$rows = $db->query_answer($query);

foreach ($rows as $row) {
    array_push($words, $row["word"]);
}

$query = "SELECT `url`FROM `photo` WHERE `user_id` = ${user['id']}";

$photos = [];
$rows = $db->query_answer($query);

foreach ($rows as $row) {
    array_push($photos, $row["url"]);
}


$user["words"] = $words;
$user["photos"] = $photos;

http_response_code(200);
echo json_encode($user);
