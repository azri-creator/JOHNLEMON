// Shared timing + map camera config (global seconds). Classic script: defines window.AKG.
window.AKG = {
  DUR: 68.5,

  // windows where the 3D map layer is on screen
  mapOn: [
    [1.35, 5.95],
    [6.35, 11.2],
  ],

  // brand
  brand: { orange: "#ff661f", purple: "#240064", purple2: "#352540", ink: "#23172f", lilac: "#bba9ce", mist: "#e8e3ed" },

  // border colours by neighbour (neon, colour-coded like the reference)
  borderColor: { FR: "#19e3ff", DE: "#ffe14a", IT: "#55ff8e", AT: "#ff4f6d", LI: "#ffffff" },
  borderName: { FR: "PERANCIS", DE: "JERMAN", IT: "ITALI", AT: "AUSTRIA", LI: "LIECHTENSTEIN" },

  // camera keys: t, target lon/lat, distance (km, mercator), pitch (deg above horizon), heading (deg), shiftX (px), ease of segment INTO this key
  cam: [
    { t: 1.4, lon: 8.2, lat: 47.6, d: 2500, p: 66, h: 0, sx: 0, e: "io" },
    { t: 5.3, lon: 8.2, lat: 46.85, d: 640, p: 51, h: -12, sx: -120, e: "io" },
    { t: 6.3, lon: 8.2, lat: 46.85, d: 600, p: 50, h: -4, sx: -120, e: "out" },
    { t: 9.4, lon: 8.43, lat: 46.80, d: 40, p: 54, h: 30, sx: -90, e: "io" },
    { t: 10.6, lon: 8.435, lat: 46.785, d: 32, p: 48, h: 44, sx: -90, e: "out" },
  ],

  // projected map labels. kind: city | major | nbr
  labels: [
    { poi: "zurich", t0: 4.0, t1: 5.5, kind: "city" },
    { poi: "bern", t0: 4.15, t1: 5.5, kind: "city" },
    { poi: "geneva", t0: 4.3, t1: 5.5, kind: "city" },
    { poi: "lugano", t0: 4.45, t1: 5.5, kind: "city" },
    { poi: "basel", t0: 4.6, t1: 5.5, kind: "city" },
    { poi: "lucerne", t0: 4.75, t1: 5.5, kind: "city" },
    { poi: "titlis", t0: 7.5, t1: 10.5, kind: "major", text: "MT TITLIS" },
    { poi: "engelberg", t0: 8.6, t1: 10.5, kind: "city", text: "ENGELBERG" },
  ],
  nbrLabels: { t0: 3.7, t1: 5.5 },
};
