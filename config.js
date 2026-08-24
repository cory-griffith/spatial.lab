/*
  Optional Mapbox story-map configuration.
  Replace the placeholder style URL and token with your own Mapbox values before using this file.
  Do not commit a secret/private token to a public repository.
*/
config = {
  style: 'mapbox://styles/YOUR_MAPBOX_USERNAME/YOUR_STYLE_ID',
  accessToken: 'YOUR_MAPBOX_PUBLIC_ACCESS_TOKEN',
  showMarkers: true,
  markerColor: '#126B73',
  theme: 'dark',
  use3dTerrain: false,
  footer: '',
  chapters: [
    {
      id: 'professional-experience',
      alignment: 'center',
      hidden: false,
      headtitle: 'Professional Experience',
      description: 'Configure this chapter when you are ready to add an interactive professional-experience map.',
      location: {
        center: [-98.5795, 39.8283],
        zoom: 3,
        pitch: 0,
        bearing: 0
      },
      mapAnimation: 'flyTo',
      rotateAnimation: false,
      callback: '',
      onChapterEnter: [],
      onChapterExit: []
    }
  ]
};