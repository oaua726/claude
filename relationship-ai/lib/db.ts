import Database from "better-sqlite3";
import path from "path";
import fs from "fs";
import type { Person, Interaction } from "./types";

const dataDir = path.join(process.cwd(), "data");
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });

const db = new Database(path.join(dataDir, "db.sqlite"));

db.exec(`
  CREATE TABLE IF NOT EXISTS persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tags TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    date TEXT NOT NULL,
    content TEXT NOT NULL,
    promises TEXT DEFAULT '',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

export function getPersons(): Person[] {
  return db.prepare("SELECT * FROM persons ORDER BY created_at DESC").all() as Person[];
}

export function getPerson(id: number): Person | undefined {
  return db.prepare("SELECT * FROM persons WHERE id = ?").get(id) as Person | undefined;
}

export function createPerson(name: string, tags: string, notes: string): Person {
  const stmt = db.prepare("INSERT INTO persons (name, tags, notes) VALUES (?, ?, ?)");
  const result = stmt.run(name, tags, notes);
  return getPerson(result.lastInsertRowid as number)!;
}

export function deletePerson(id: number): void {
  db.prepare("DELETE FROM persons WHERE id = ?").run(id);
}

export function getInteractions(personId: number): Interaction[] {
  return db
    .prepare("SELECT * FROM interactions WHERE person_id = ? ORDER BY date DESC, created_at DESC")
    .all(personId) as Interaction[];
}

export function createInteraction(
  personId: number,
  date: string,
  content: string,
  promises: string
): Interaction {
  const stmt = db.prepare(
    "INSERT INTO interactions (person_id, date, content, promises) VALUES (?, ?, ?, ?)"
  );
  const result = stmt.run(personId, date, content, promises);
  return db
    .prepare("SELECT * FROM interactions WHERE id = ?")
    .get(result.lastInsertRowid) as Interaction;
}

export function deleteInteraction(id: number): void {
  db.prepare("DELETE FROM interactions WHERE id = ?").run(id);
}
