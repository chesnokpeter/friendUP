<?php

require 'database.php';

$input = json_decode(file_get_contents("php://input"), true);

$id = $input['seeker_id'];
$words = $input['words'];

$check = is_null($id) || is_null($words);
if ($check) {
    echo json_encode(["message" => "Не все нужные параметры были переданы"]);
    die();
}

foreach ($words as &$word) {
    $word = "'${word}'";
}

$words_string = join(",", $words);



$query = <<<EOT
    SELECT `user`.`id` FROM `key_word`
    JOIN `user` ON `key_word`.`user_id` = `user`.`id`
    JOIN `status` ON `user`.`status_id` = `status`.`id`
    WHERE `user`.`id` != ${id} AND `word` IN (${words_string})
    ORDER BY RAND()
    LIMIT 1
EOT;

$db = new DataBase();
$db->connect();

$row = $db->query_answer($query);


if (is_null($row[0]["id"])) {
    echo json_encode(["message" => "Для этих ключевых слов не удалось найти подходящего кандидата"]);
    die();
}

$user_id = $row[0]["id"];

// ----------------

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
