
window.config = {
  routerBasename: '/',
  extensions: [],
  modes: [],
  showStudyList: true,

  dataSources: [
    {
      namespace: '@ohif/extension-default.dataSourcesModule.dicomweb',
      sourceName: 'orthanc',
      configuration: {
        friendlyName: 'Orthanc PACS',
        name: 'ORTHANC',

        qidoRoot: 'http://localhost:8080/dicom-web',
	      wadoRoot: 'http://localhost:8080/dicom-web',
	      wadoUriRoot: 'http://localhost:8080/wado',

        qidoSupportsIncludeField: false,
        supportsReject: false,

        imageRendering: 'wadors',
        thumbnailRendering: 'wadors',

        enableStudyLazyLoad: true,
        supportsFuzzyMatching: false,
        supportsWildcard: true,
      },
    },
  ],

  defaultDataSourceName: 'orthanc',
};
