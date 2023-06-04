<?php
header("Content-Type: text/html; charset=UTF-8");
class DataBase
{
	public $HOST_DB = "localhost";
	private $NAME_DB = ""; // имя базы данных
	private $USER = ""; // имя пользователя
	private $PASSWORD = ""; // пароль

	private $DB = null; //? Основной объект БД

	public function connect()
	{
		try {
			$this->DB = new PDO("mysql:host={$this->HOST_DB};dbname={$this->NAME_DB}", $this->USER, $this->PASSWORD);
			$this->DB->query('SET CHARACTER SET utf8');
		} catch (PDOException $err) {
			echo "[!!!] Ошибка! База данных недоступна... ";
			$this->DB = null;
		};
	}

	public function check()
	{
		return $this->DB == null ? false : true;
	}


	public function query_answer($query)
	{
		if ($this->DB) {
			$result = $this->DB->query($query);
			return $result ? $result->fetchAll(PDO::FETCH_ASSOC) : false;
		} else {
			echo "[!!!] Ошибка! База данных недоступна... ";
		}
	}

	public function query_not_answer($query)
	{
		if ($this->DB) {
			return $this->DB->exec($query);
		} else {
			echo "[!!!] Ошибка! База данных недоступна... ";
		}
	}
}
