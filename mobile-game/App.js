import React, { useCallback, useEffect, useReducer, useRef } from 'react';
import {
  Dimensions,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StatusBar } from 'expo-status-bar';

// ---------------------------------------------------------------------------
// Robot Runner — an endless "flap to fly" game.
// Tap anywhere to make the robot flap upward; gravity pulls it down.
// Fly through the gaps between obstacles. One touch = game over.
// ---------------------------------------------------------------------------

const { width: SCREEN_W, height: SCREEN_H } = Dimensions.get('window');

// The play area is capped so the game feels the same on a wide browser window
// as it does on a phone screen.
const GAME_W = Math.min(SCREEN_W, 480);
const GAME_H = SCREEN_H;

// --- Tunable game constants (all distances in px, time in seconds) ---
const GRAVITY = 1600; // downward acceleration
const FLAP_VELOCITY = -480; // instant upward velocity on tap
const ROBOT_SIZE = 46;
const ROBOT_X = GAME_W * 0.28; // robot stays at a fixed horizontal spot
const OBSTACLE_WIDTH = 66;
const GAP_HEIGHT = 210; // vertical opening the robot flies through
const OBSTACLE_SPEED = 190; // how fast obstacles scroll left
const OBSTACLE_SPACING = 260; // horizontal distance between obstacles
const GROUND_HEIGHT = 70;
const MIN_GAP_TOP = 60; // keep gaps away from the very top/bottom
const HIGH_SCORE_KEY = '@robot_runner_high_score';

const STATE = { READY: 'READY', PLAYING: 'PLAYING', OVER: 'OVER' };

function randomGapTop() {
  const maxTop = GAME_H - GROUND_HEIGHT - GAP_HEIGHT - MIN_GAP_TOP;
  return MIN_GAP_TOP + Math.random() * Math.max(0, maxTop - MIN_GAP_TOP);
}

function freshGame() {
  return {
    status: STATE.READY,
    robotY: GAME_H * 0.4,
    velocity: 0,
    obstacles: [], // { x, gapTop, scored }
    score: 0,
    spawnX: GAME_W, // x of the next obstacle to spawn
  };
}

export default function App() {
  // All fast-changing game state lives in a ref so the rAF loop never reads a
  // stale closure; `tick` just forces React to re-render each animation frame.
  const game = useRef(freshGame());
  const [, forceRender] = useReducer((n) => n + 1, 0);
  const highScore = useRef(0);
  const rafRef = useRef(null);
  const lastTs = useRef(0);

  // Load the persisted high score once on mount.
  useEffect(() => {
    AsyncStorage.getItem(HIGH_SCORE_KEY)
      .then((v) => {
        if (v != null) {
          highScore.current = parseInt(v, 10) || 0;
          forceRender();
        }
      })
      .catch(() => {});
  }, []);

  const persistHighScore = useCallback((score) => {
    if (score > highScore.current) {
      highScore.current = score;
      AsyncStorage.setItem(HIGH_SCORE_KEY, String(score)).catch(() => {});
    }
  }, []);

  const step = useCallback(
    (ts) => {
      const g = game.current;
      if (lastTs.current === 0) lastTs.current = ts;
      // Clamp dt so a paused/backgrounded tab doesn't teleport the robot.
      const dt = Math.min((ts - lastTs.current) / 1000, 0.05);
      lastTs.current = ts;

      if (g.status === STATE.PLAYING) {
        // Physics
        g.velocity += GRAVITY * dt;
        g.robotY += g.velocity * dt;

        // Move obstacles left
        for (const o of g.obstacles) o.x -= OBSTACLE_SPEED * dt;

        // Spawn new obstacles as the field scrolls
        const last = g.obstacles[g.obstacles.length - 1];
        if (!last || last.x <= GAME_W - OBSTACLE_SPACING) {
          g.obstacles.push({ x: GAME_W, gapTop: randomGapTop(), scored: false });
        }

        // Drop obstacles that have fully left the screen
        if (g.obstacles.length && g.obstacles[0].x < -OBSTACLE_WIDTH) {
          g.obstacles.shift();
        }

        // Scoring + collision
        const robotTop = g.robotY;
        const robotBottom = g.robotY + ROBOT_SIZE;
        const robotLeft = ROBOT_X;
        const robotRight = ROBOT_X + ROBOT_SIZE;

        for (const o of g.obstacles) {
          if (!o.scored && o.x + OBSTACLE_WIDTH < robotLeft) {
            o.scored = true;
            g.score += 1;
          }
          const overlapX = robotRight > o.x && robotLeft < o.x + OBSTACLE_WIDTH;
          const inGap = robotTop > o.gapTop && robotBottom < o.gapTop + GAP_HEIGHT;
          if (overlapX && !inGap) {
            g.status = STATE.OVER;
            persistHighScore(g.score);
          }
        }

        // Floor / ceiling
        if (robotBottom >= GAME_H - GROUND_HEIGHT) {
          g.robotY = GAME_H - GROUND_HEIGHT - ROBOT_SIZE;
          g.status = STATE.OVER;
          persistHighScore(g.score);
        }
        if (robotTop <= 0) {
          g.robotY = 0;
          g.velocity = 0;
        }
      }

      forceRender();
      rafRef.current = requestAnimationFrame(step);
    },
    [persistHighScore]
  );

  useEffect(() => {
    rafRef.current = requestAnimationFrame(step);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [step]);

  const onTap = useCallback(() => {
    const g = game.current;
    if (g.status === STATE.READY) {
      g.status = STATE.PLAYING;
      g.velocity = FLAP_VELOCITY;
    } else if (g.status === STATE.PLAYING) {
      g.velocity = FLAP_VELOCITY;
    } else if (g.status === STATE.OVER) {
      game.current = freshGame();
    }
  }, []);

  const g = game.current;
  // Tilt the robot with its velocity for a bit of life.
  const tilt = Math.max(-25, Math.min(60, g.velocity * 0.06));

  return (
    <Pressable style={styles.root} onPress={onTap}>
      <StatusBar style="light" />
      <View style={[styles.game, { width: GAME_W, height: GAME_H }]}>
        {/* Parallax-ish background stars */}
        <Stars />

        {/* Obstacles */}
        {g.obstacles.map((o, i) => (
          <React.Fragment key={i}>
            <View
              style={[
                styles.obstacle,
                { left: o.x, top: 0, height: o.gapTop, width: OBSTACLE_WIDTH },
              ]}
            />
            <View
              style={[
                styles.obstacle,
                {
                  left: o.x,
                  top: o.gapTop + GAP_HEIGHT,
                  height: GAME_H - (o.gapTop + GAP_HEIGHT) - GROUND_HEIGHT,
                  width: OBSTACLE_WIDTH,
                },
              ]}
            />
          </React.Fragment>
        ))}

        {/* Ground */}
        <View style={[styles.ground, { height: GROUND_HEIGHT }]} />

        {/* Robot */}
        <View
          style={[
            styles.robot,
            {
              left: ROBOT_X,
              top: g.robotY,
              transform: [{ rotate: `${tilt}deg` }],
            },
          ]}
        >
          <Text style={styles.robotEmoji}>🤖</Text>
        </View>

        {/* Score (during play) */}
        {g.status === STATE.PLAYING && (
          <Text style={styles.scoreLive}>{g.score}</Text>
        )}

        {/* Ready overlay */}
        {g.status === STATE.READY && (
          <View style={styles.overlay} pointerEvents="none">
            <Text style={styles.title}>ROBOT RUNNER</Text>
            <Text style={styles.subtitle}>Tapni za let</Text>
            <Text style={styles.hint}>
              Izogibaj se oviram in leti čim dlje 🤖
            </Text>
          </View>
        )}

        {/* Game over overlay */}
        {g.status === STATE.OVER && (
          <View style={styles.overlay} pointerEvents="none">
            <Text style={styles.title}>KONEC IGRE</Text>
            <Text style={styles.bigScore}>{g.score}</Text>
            <Text style={styles.subtitle}>Najboljši: {highScore.current}</Text>
            <Text style={styles.hint}>Tapni za novo igro</Text>
          </View>
        )}
      </View>
    </Pressable>
  );
}

// Static decorative star field, memoised so it isn't recomputed each frame.
const STARS = Array.from({ length: 40 }, () => ({
  left: Math.random() * GAME_W,
  top: Math.random() * (GAME_H - GROUND_HEIGHT),
  size: Math.random() < 0.8 ? 2 : 3,
  opacity: 0.3 + Math.random() * 0.6,
}));

function Stars() {
  return (
    <>
      {STARS.map((s, i) => (
        <View
          key={i}
          style={{
            position: 'absolute',
            left: s.left,
            top: s.top,
            width: s.size,
            height: s.size,
            borderRadius: s.size,
            backgroundColor: '#ffffff',
            opacity: s.opacity,
          }}
        />
      ))}
    </>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#0b1026',
    alignItems: 'center',
    justifyContent: 'center',
    ...(Platform.OS === 'web' ? { cursor: 'pointer', userSelect: 'none' } : {}),
  },
  game: {
    backgroundColor: '#0b1026',
    overflow: 'hidden',
    position: 'relative',
  },
  robot: {
    position: 'absolute',
    width: ROBOT_SIZE,
    height: ROBOT_SIZE,
    alignItems: 'center',
    justifyContent: 'center',
  },
  robotEmoji: {
    fontSize: ROBOT_SIZE - 6,
    lineHeight: ROBOT_SIZE,
  },
  obstacle: {
    position: 'absolute',
    backgroundColor: '#3ddc97',
    borderColor: '#2bb47a',
    borderWidth: 3,
    borderRadius: 6,
  },
  ground: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#1c2547',
    borderTopColor: '#3ddc97',
    borderTopWidth: 3,
  },
  scoreLive: {
    position: 'absolute',
    top: 60,
    alignSelf: 'center',
    fontSize: 52,
    fontWeight: '800',
    color: '#ffffff',
    textShadowColor: 'rgba(0,0,0,0.5)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  overlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
    paddingBottom: GROUND_HEIGHT,
  },
  title: {
    fontSize: 40,
    fontWeight: '900',
    color: '#3ddc97',
    letterSpacing: 2,
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 20,
    color: '#ffffff',
    marginBottom: 8,
  },
  bigScore: {
    fontSize: 72,
    fontWeight: '900',
    color: '#ffffff',
    marginVertical: 8,
  },
  hint: {
    fontSize: 15,
    color: '#9aa4c7',
    marginTop: 10,
    textAlign: 'center',
    paddingHorizontal: 30,
  },
});
