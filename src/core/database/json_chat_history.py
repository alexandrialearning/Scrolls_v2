import json
from pathlib import Path
from typing import Any, Dict, List, Optional

CHAT_HISTORY_FILE = Path("data/silver/chat_history.json")

class JsonChatHistory:
	"""Code made by GPT-5.1-Codex and revised by Ali Campos"""

	def __init__(self, file_path: Optional[Path] = None) -> None:
		self.file_path = Path(file_path) if file_path else CHAT_HISTORY_FILE
		self.file_path.parent.mkdir(parents=True, exist_ok=True)


	def add_responses(self, user_id: str, message: str, response: str) -> None:
		"""Agrega un par mensaje-respuesta para un usuario."""
		data = self._load()
		user_history = data.setdefault(user_id, [])
		user_history.append({"message": message, "response": response})
		self._save(data)


	def get_last_responses(self, user_id: str, n: int) -> List[Dict[str, Any]]:
		"""Regresa las últimas n respuestas de un usuario (ordenadas del más reciente al más antiguo)."""
		if n <= 0:
			return []
		history = self._load().get(user_id, [])
		return list(reversed(history[-n:]))


	def delete_last_responses(self, user_id: str, n: int) -> int:
		"""Elimina las últimas n respuestas de un usuario y regresa cuántas se eliminaron."""
		if n <= 0:
			return 0
		data = self._load()
		history = data.get(user_id, [])
		if not history:
			return 0

		removed = min(n, len(history))
		del history[-removed:]
		if history:
			data[user_id] = history
		else:
			data.pop(user_id, None)
		self._save(data)
		return removed


	def _load(self) -> Dict[str, List[Dict[str, str]]]:
		if not self.file_path.exists():
			return {}
		with self.file_path.open("r", encoding="utf-8") as f:
			try:
				return json.load(f)
			except json.JSONDecodeError:
				return {}


	def _save(self, data: Dict[str, List[Dict[str, str]]]) -> None:
		with self.file_path.open("w", encoding="utf-8") as f:
			json.dump(data, f, ensure_ascii=False, indent=2)
