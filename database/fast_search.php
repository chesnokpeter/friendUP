<?php

require 'database.php';

// ini_set('error_reporting', E_ALL);
// ini_set('display_errors', 1);
// ini_set('display_startup_errors', 1);

$id = $_GET['id'];
if (!is_numeric($id)) {
    echo json_encode(["message" => "Важно передовать только число"]);
    die();
}

$query = <<<EOT
    SELECT `user`.`id` FROM `user`
    WHERE `user`.`id` != ${id}
    ORDER BY RAND()
    LIMIT 1
EOT;

$db = new DataBase();
$db->connect();

$row = $db->query_answer($query);

if (is_null($row[0]["id"])) {
    echo json_encode(["message" => "Не удалось найти случайного кандидата"]);
    die();
}

$user_id = $row[0]["id"];


// ----------------------
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
    WHERE `user`.`id` = ${user_id} LIMIT 1
EOT;

$user = [];
$row = $db->query_answer($query);
$user = $row[0];

$query = "SELECT `word`FROM `key_word` WHERE `user_id` = ${user_id}";

$words = [];
$rows = $db->query_answer($query);

foreach ($rows as $row) {
    array_push($words, $row["word"]);
}

$query = "SELECT `url`FROM `photo` WHERE `user_id` = ${user_id}";

$photos = [];
$rows = $db->query_answer($query);

foreach ($rows as $row) {
    array_push($photos, $row["url"]);
}


$user["words"] = $words;
$user["photos"] = $photos;

http_response_code(200);
echo json_encode($user);
