<?php
require 'database.php';

$input = json_decode(file_get_contents("php://input"), true);

$telegram_chat_id = $input['telegram_chat_id'];
$text = $input['text'];
$status_id = $input['status_id'];
$telegram_name = $input['telegram_name'];
$age = $input['age'];
$city = $input['city'];
$words = $input['words'];
$photos = $input['photos'];
$name = $input['name'];


$check = is_null($telegram_chat_id)
    || is_null($text)
    || is_null($status_id)
    || is_null($telegram_name)
    || is_null($age)
    || is_null($city)
    || is_null($words)
    || is_null($photos)
    || is_null($name);

if ($check) {
    echo json_encode(["message" => "Не все нужные параметры были переданы"]);
    die();
}

$query = <<<EOT
INSERT INTO `user` (    
    `id`, 
    `telegram_chat_id`, 
    `text`, 
    `status_id`, 
    `telegram_name`, 
    `age`, 
    `city`, 
    `name` ) 
    VALUES ( NULL, '${telegram_chat_id}', '${text}', ${status_id}, '${telegram_name}', ${age}, '${city}', '${name}' );
EOT;


$db = new DataBase();
$db->connect();

$result = $db->query_not_answer($query);



if ($result == 1) {
    // если запись добавилась успешно
    $user_id = $db->query_answer("SELECT LAST_INSERT_ID() AS ID;")[0]["ID"];


    // добавление слов
    foreach ($words as $word) {
        $lower = trim(mb_strtolower($word));
        $query_word = "INSERT INTO `key_word` (`id`, `word`, `user_id`) VALUES (NULL, '${lower}', ${user_id})";
        $result = $db->query_not_answer($query_word);
    }

    // добавление фото
    foreach ($photos as $url) {
        $query_url = "INSERT INTO `photo` (`id`, `url`, `user_id`) VALUES (NULL, '${url}', '${user_id}')";
        $result = $db->query_not_answer($query_url);
    }

    http_response_code(200);
    echo json_encode(["id" => $user_id]);
} else {
    http_response_code(400);
    echo json_encode(["message" => "Данные не добалены в БД"]);
}
