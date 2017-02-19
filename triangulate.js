var fs = require('fs');
var triangulate = require('triangulate-image');

var params = {
        accuracy: 0.7,
        blur: 4,
        fill: true,
        stroke: true,
        strokeWidth: 0.5,
        lineJoin: 'miter',
        vertexCount: 50,
        threshold: 50,
        gradients: false
};

fromBufferToData();

function fromBufferToData () {
        fs.readFile( __dirname + '/' + process.argv[2], function ( err, buffer ) {
                    if ( err ) {
                                    throw err;
                                }
                    
                    triangulate( params )
                        .fromBuffer( buffer )
                        .toData()
                        .then ( function ( data ) {
                                            var dataStr = JSON.stringify( data, null, '  ' );

                                            fs.writeFile( __dirname + '/json-out/data.json', dataStr, function ( err ) {
                                                                    if ( err ) {
                                                                                                throw err;
                                                                                            } else {
                                                                                                console.log( 'fromBufferToData complete.' );
                                                                                            }
                                                                } );
                                        } );
                } );
}
