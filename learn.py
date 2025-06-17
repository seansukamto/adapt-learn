import streamlit as st
from utils.database import DatabaseManager
from utils.adaptive_logic import AdaptiveEngine
import random
from config.settings import APP_CONFIG

import streamlit.components.v1 as components

db = DatabaseManager()
adaptive_engine = AdaptiveEngine()

def show():
    st.header("📚 Learning Hub")

    subjects = APP_CONFIG["subjects"]
    subj = st.selectbox("Subject", list(subjects.keys()))
    topic = st.selectbox("Topic", subjects[subj])

    # --- Webcam drag-and-drop interaction ---

    if subj == "Science" and topic == "Biology":
      components.html("""
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>Genetics Drag and Drop</title>
        <style>
          body { font-family: sans-serif; margin: 0; padding: 20px; }
          .container { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
          .flower, .zone, .child {
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            border-radius: 8px;
            cursor: grab;
            user-select: none;
          }
          .flower { border: 2px solid black; }
          .zone { background: #eee; color: white; border: 2px dashed #aaa; }
          .label { width: 100px; font-weight: bold; }
          #children-container { display: flex; align-items: center; margin-top: 20px; gap: 10px; }
          #children { display: flex; gap: 10px; flex-wrap: wrap; }
        </style>
      </head>
      <body>

      <h3>Drag one flower into the Parent A slot and one flower into the Parent B slot to explore inheritance.</h3>

      <div class="container" id="flowers">
        <div class="flower" draggable="true" data-geno="PP" style="background: purple;">PP</div>
        <div class="flower" draggable="true" data-geno="PP" style="background: purple;">PP</div>
        <div class="flower" draggable="true" data-geno="Pp" style="background: orchid;">Pp</div>
        <div class="flower" draggable="true" data-geno="Pp" style="background: orchid;">Pp</div>
        <div class="flower" draggable="true" data-geno="pp" style="background: lightgray;">pp</div>
        <div class="flower" draggable="true" data-geno="pp" style="background: lightgray;">pp</div>
      </div>

      <br>

      <div class="container">
        <div class="label">Parents:</div>
        <div class="zone" id="parentA" ondragover="event.preventDefault()" ondrop="drop(event, 'A')" style="color: gray;">Parent A</div>
        <div class="zone" id="parentB" ondragover="event.preventDefault()" ondrop="drop(event, 'B')" style="color: gray;">Parent B</div>
      </div>

      <div id="children-container">
        <div class="label">Offspring:</div>
        <div id="children"></div>
      </div>

      <script>
      let parents = { A: null, B: null };
      const colors = { PP: 'purple', Pp: 'orchid', pp: 'gray' };

      document.querySelectorAll('.flower').forEach(f => {
        f.addEventListener('dragstart', (e) => {
          e.dataTransfer.setData('text/plain', f.dataset.geno);
        });
      });

      function drop(e, zone) {
        const geno = e.dataTransfer.getData('text/plain');
        parents[zone] = geno;

        const box = document.getElementById('parent' + zone);
        box.textContent = geno;
        box.style.background = colors[geno] || '#eee';

        if (parents.A && parents.B) showChildren();
      }

      function getAlleles(geno) {
        return geno === 'PP' ? ['P','P'] :
              geno === 'Pp' ? ['P','p'] :
              ['p','p'];
      }

      function showChildren() {
        const a = getAlleles(parents.A);
        const b = getAlleles(parents.B);
        const combos = [];

        for (let i=0; i<2; i++) {
          for (let j=0; j<2; j++) {
            let genes = [a[i], b[j]].sort().join('');
            combos.push(genes === 'PP' ? 'PP' : genes === 'Pp' ? 'Pp' : 'pp');
          }
        }

        const out = combos.map(g =>
          `<div class='child flower' style='background:${colors[g]}'>${g}</div>`
        ).join('');
        document.getElementById('children').innerHTML = out;
      }
      </script>

      </body>
      </html>
      """, height=520)


      
    elif subj == "Science" and topic == "Chemistry":

      st.subheader("🧪🖐️ Drag both H₂ to O₂ to React")

      components.html("""
      <!DOCTYPE html>
      <html>
      <head>
        <style>
          video, canvas {
            position: absolute;
            top: 0;
            left: 0;
          }
          #wrapper {
            position: relative;
            width: 640px;
            height: 480px;
          }
          .label {
            position: absolute;
            font-weight: bold;
            color: white;
            text-align: center;
            width: 80px;
            pointer-events: none;
          }
        </style>
      </head>
      <body>
      <div id="wrapper">
        <video id="video" width="640" height="480" autoplay playsinline muted></video>
        <canvas id="canvas" width="640" height="480"></canvas>
      </div>

      <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>

      <script>
      const video = document.getElementById("video");
      const canvas = document.getElementById("canvas");
      const ctx = canvas.getContext("2d");

      let draggingBox = null;
      let reacted = false;

      // Initial state: 2 H2 and 1 O2
      let boxes = [
        { id: "H1", label: "H₂", x: 100, y: 150, size: 80, color: "red", type: "H" },
        { id: "H2", label: "H₂", x: 200, y: 300, size: 80, color: "red", type: "H" },
        { id: "O", label: "O₂", x: 400, y: 200, size: 80, color: "blue", type: "O" }
      ];

      function drawScene(landmarks) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        for (const box of boxes) {
          ctx.fillStyle = box.color;
          ctx.fillRect(box.x, box.y, box.size, box.size);

          // Draw label
          ctx.fillStyle = "white";
          ctx.font = "bold 20px sans-serif";
          ctx.textAlign = "center";
          ctx.fillText(box.label, box.x + box.size / 2, box.y + box.size / 2 + 8);
        }

        if (landmarks) {
          for (const point of landmarks) {
            ctx.beginPath();
            ctx.arc(point.x * canvas.width, point.y * canvas.height, 5, 0, 2 * Math.PI);
            ctx.fillStyle = "lime";
            ctx.fill();
          }
        }
      }

      function isPinching(landmarks) {
        const dx = landmarks[4].x - landmarks[8].x;
        const dy = landmarks[4].y - landmarks[8].y;
        return Math.sqrt(dx * dx + dy * dy) < 0.05;
      }

      function checkOverlap(boxA, boxB) {
        return (
          boxA.x < boxB.x + boxB.size &&
          boxA.x + boxA.size > boxB.x &&
          boxA.y < boxB.y + boxB.size &&
          boxA.y + boxA.size > boxB.y
        );
      }

      function handleReaction() {
        const hBoxes = boxes.filter(b => b.type === "H");
        const oBox = boxes.find(b => b.type === "O");

        if (!oBox || hBoxes.length < 2) return false;

        const overlap1 = checkOverlap(hBoxes[0], oBox);
        const overlap2 = checkOverlap(hBoxes[1], oBox);

        return overlap1 && overlap2;
      }

      function reactToWater() {
        boxes = [
          { id: "H2O1", label: "H₂O", x: 200, y: 150, size: 100, color: "green", type: "H2O" },
          { id: "H2O2", label: "H₂O", x: 300, y: 250, size: 100, color: "green", type: "H2O" }
        ];
        reacted = true;
      }

      function updateDragging(landmarks) {
        const x = landmarks[8].x * canvas.width;
        const y = landmarks[8].y * canvas.height;

        if (draggingBox && isPinching(landmarks)) {
          draggingBox.x = x - draggingBox.size / 2;
          draggingBox.y = y - draggingBox.size / 2;
        } else {
          draggingBox = null;
          if (!reacted && isPinching(landmarks)) {
            for (let box of boxes) {
              if (
                x >= box.x && x <= box.x + box.size &&
                y >= box.y && y <= box.y + box.size
              ) {
                draggingBox = box;
                break;
              }
            }
          }
        }

        if (!reacted && handleReaction()) {
          reactToWater();
        }
      }

      const hands = new Hands({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });

      hands.setOptions({
        maxNumHands: 1,
        modelComplexity: 1,
        minDetectionConfidence: 0.7,
        minTrackingConfidence: 0.5,
      });

      hands.onResults((results) => {
        if (results.multiHandLandmarks.length > 0) {
          const landmarks = results.multiHandLandmarks[0];
          updateDragging(landmarks);
          drawScene(landmarks);
        } else {
          drawScene(null);
          draggingBox = null;
        }
      });

      const camera = new Camera(video, {
        onFrame: async () => await hands.send({ image: video }),
        width: 640,
        height: 480,
      });
      camera.start();
      </script>
      </body>
      </html>
      """, height=500)
