# ADR 008 — No arbitrary file CRUD

禁止通用 `PUT /file`、`POST /yaml`、`DELETE /markdown`。路径由稳定对象 ID 与 operation 在服务器解析。
