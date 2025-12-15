// Constraints de ejemplo
CREATE CONSTRAINT IF NOT EXISTS
FOR (e:Exercise) REQUIRE e.name IS UNIQUE;

// Semillas mínimas (opcional)
MERGE (:TrainingType {name:"Running"});
