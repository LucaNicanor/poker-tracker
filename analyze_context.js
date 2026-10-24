const fs = require('fs');
const path = require('path');

const RAW_DIR = path.join(__dirname, 'hands', 'raw');
const PROCESSED_DIR = path.join(__dirname, 'hands', 'processed');

// 1. Analyze GTO Wizard PokerArena hands
const gtowData = JSON.parse(fs.readFileSync(path.join(RAW_DIR, 'gtowizard_pokerarena_hands.json'), 'utf8'));

let gtowTotalHands = gtowData.length;
let gtowEvLossTotal = 0;
let gtowMistakes = [];
let gtowPosStats = { SB: { hands: 0, evLoss: 0 }, BB: { hands: 0, evLoss: 0 } };

gtowData.forEach((row, idx) => {
  // Typical row: ["9/17/2026", "HU SnG", "SB", "Q", "4", "T", "7", "3", "Q", "8", "SRP", "RC", ... EV loss, GTOW Score ...]
  const pos = row[2]; // "SB" or "BB"
  if (gtowPosStats[pos]) {
    gtowPosStats[pos].hands++;
  }

  // Find numerical EV loss and GTOW score
  let evLoss = 0;
  let score = 0;
  let potType = row.find(x => ['Preflop', 'SRP', 'Limp', '3-Bet', '3-bet', 'ISO'].includes(x)) || 'Unknown';
  let cards = `${row[3]}${row[4]}`;

  // Find EV loss column
  for (let i = 5; i < row.length; i++) {
    const val = parseFloat(row[i]);
    // Look for EV loss pattern: typically small float e.g. 0.51, 0.27, 0.28, 0.09
    if (row[i-1] && (row[i-1].includes('RC') || row[i-1].includes('BC') || row[i-1].includes('BF') || row[i-1].includes('XX') || !isNaN(parseFloat(row[i-1])))) {
      // Check if row has explicit EV loss
    }
  }

  // More direct search in the row for EV loss
  // If we inspect row structure:
  // e.g. row: ["9/17/2026", "HU SnG", "SB", "Q", "4", "Preflop", "F", "1.5", "-0.5", "0.09", "5.9", "-100", "78.1", "10/20", "lucatricari", "25", "2", "PokerArena"]
  // Here 0.09 is EV loss, 5.9 is %pot loss, -100 is score, 78.1 is freq diff.
  // Another row: ["9/17/2026", "HU SnG", "SB", "A", "3", "Preflop", "RF", "26", "1", "0.27", "18.3", "-100", "72.1", "10/20", "lucatricari", "25", "2", "PokerArena"]
  // 0.27 is EV loss, 18.3 is EV loss pot%, -100 is score, 72.1 is freq diff.
  
  // Let's find index of "lucatricari"
  const lucaIdx = row.indexOf('lucatricari');
  if (lucaIdx !== -1) {
    // Usually stakes is at lucaIdx - 1 ("10/20")
    // freqDiff is at lucaIdx - 2
    // score is at lucaIdx - 3
    // evLossPot is at lucaIdx - 4
    // evLoss is at lucaIdx - 5
    const parsedEvLoss = parseFloat(row[lucaIdx - 5]);
    const parsedEvLossPot = parseFloat(row[lucaIdx - 4]);
    const parsedScore = parseFloat(row[lucaIdx - 3]);
    const parsedFreqDiff = parseFloat(row[lucaIdx - 2]);

    if (!isNaN(parsedEvLoss) && parsedEvLoss > 0) {
      gtowEvLossTotal += parsedEvLoss;
      if (gtowPosStats[pos]) gtowPosStats[pos].evLoss += parsedEvLoss;
      gtowMistakes.push({
        handIdx: idx + 1,
        date: row[0],
        pos,
        cards,
        potType,
        evLoss: parsedEvLoss,
        evLossPot: parsedEvLossPot,
        score: parsedScore,
        freqDiff: parsedFreqDiff,
        fullRow: row
      });
    }
  }
});

gtowMistakes.sort((a, b) => b.evLoss - a.evLoss);

// 2. Analyze PokerNow hands
const pnFiles = ['pn_practice_oct15_A.json', 'pn_practice_oct15_B.json', 'pn_practice_oct15_C.json', 'pn_practice_oct15_D.json'];
let pnTotalHands = 0;
let lucaHandsPlayed = 0;
let lucaVoluntarilyPutMoney = 0;
let lucaPreflopRaise = 0;
let luca3Bet = 0;
let lucaPotsWon = 0;
let lucaStartingStack = 0;
let lucaEndingStack = 0;
let lucaHandSamples = [];

pnFiles.forEach(file => {
  const filePath = path.join(RAW_DIR, file);
  if (!fs.existsSync(filePath)) return;
  const content = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  const hands = content.hands || [];
  pnTotalHands += hands.length;

  hands.forEach(hand => {
    // Find Luca in this hand
    const luca = (hand.players || []).find(p => p.name.toLowerCase() === 'luca' || p.id === '2Tp9ZZJ5k2');
    if (!luca) return;

    lucaHandsPlayed++;
    const seat = luca.seat;
    const cards = luca.hand || [];

    // Check actions in hand
    let vpip = false;
    let pfr = false;
    let threeBet = false;
    let isWinner = false;

    // Parse PokerNow events
    let isPreflop = true;
    let raisesBeforeLuca = 0;

    (hand.events || []).forEach(e => {
      const p = e.payload;
      if (p.type === 9) {
        // Community cards dealt (Flop / Turn / River)
        isPreflop = false;
      }

      if (isPreflop) {
        if (p.type === 7 && p.seat !== seat) {
          raisesBeforeLuca++;
        }
        if (p.seat === seat) {
          if (p.type === 8) { // Call
            vpip = true;
          }
          if (p.type === 7) { // Raise
            vpip = true;
            pfr = true;
            if (raisesBeforeLuca >= 1) threeBet = true;
          }
        }
      }

      // Check if won pot
      if (p.type === 10 && p.seat === seat) {
        isWinner = true;
      }
    });

    if (vpip) lucaVoluntarilyPutMoney++;
    if (pfr) lucaPreflopRaise++;
    if (threeBet) luca3Bet++;
    if (isWinner) lucaPotsWon++;

    if (cards.length > 0 && lucaHandSamples.length < 10) {
      lucaHandSamples.push({
        file,
        number: hand.number,
        cards,
        pot: hand.pot,
        vpip,
        pfr,
        won: isWinner
      });
    }
  });
});

const report = {
  summary: {
    totalHandsAnalyzed: gtowTotalHands + pnTotalHands,
    gtoWizardHands: gtowTotalHands,
    pokerNowHands: pnTotalHands,
    lucaLiveHandsPlayed: lucaHandsPlayed
  },
  gtoWizardBaseline: {
    handsSampled: gtowTotalHands,
    totalEvLossBb: parseFloat(gtowEvLossTotal.toFixed(2)),
    averageEvLossPerHand: parseFloat((gtowEvLossTotal / gtowTotalHands).toFixed(3)),
    positionBreakdown: gtowPosStats,
    topBlunders: gtowMistakes.slice(0, 5)
  },
  pokerNowLiveProfile: {
    hands: lucaHandsPlayed,
    vpipPercentage: lucaHandsPlayed > 0 ? parseFloat(((lucaVoluntarilyPutMoney / lucaHandsPlayed) * 100).toFixed(1)) : 0,
    pfrPercentage: lucaHandsPlayed > 0 ? parseFloat(((lucaPreflopRaise / lucaHandsPlayed) * 100).toFixed(1)) : 0,
    threeBetPercentage: lucaHandsPlayed > 0 ? parseFloat(((luca3Bet / lucaHandsPlayed) * 100).toFixed(1)) : 0,
    winRatePotsPercentage: lucaHandsPlayed > 0 ? parseFloat(((lucaPotsWon / lucaHandsPlayed) * 100).toFixed(1)) : 0
  }
};

fs.writeFileSync(path.join(PROCESSED_DIR, 'player_context.json'), JSON.stringify(report, null, 2));
console.log('Analysis Complete!');
console.log(JSON.stringify(report, null, 2));
