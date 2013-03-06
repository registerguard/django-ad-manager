/*
	@TODO:
		1. Optimize variables (i.e. go back to putting JSON vars in JS vars).
		2. Add comments, Micky style.
		3. ...
*/
;(function($, window, document, undefined) {
	
	"use strict";
	
	var console = window.console || { log : function() {}, warn : function() {} },
	
	defaults = {
		
		api     : 'http://advertising.registerguard.com/manager/',
		parent  : '',
		section : '',
		page    : '',
		cb      : (Math.round(Math.random() * 10000000000000000)),
		
		// Should we move these to the JSON?
		units : {
			
			mobile : {
				
				'mobile-banner'      : '#mobile_banner-top',
				'medium-rectangle-1' : '#medium_rectangle_1-mobile',
				'medium-rectangle-2' : '#medium_rectangle_2-mobile',
				'homepage-block-1'   : '#homepage_block_1-mobile',
				'homepage-block-2'   : '#homepage_block_2-mobile',
				'homepage-block-3'   : '#homepage_block_3-mobile',
				'ros_column-block'   : '#column_block-mobile',
				'ros_mobile-banner'  : '#mobile_banner-bottom'
				
			},
			
			desktop : {
				
				'leaderboard'        : '#leaderboard-top',
				'medium-rectangle-1' : '#medium_rectangle_1-desktop',
				'medium-rectangle-2' : '#medium_rectangle_2-desktop',
				'homepage-block-1'   : '#homepage_block_1-desktop',
				'homepage-block-2'   : '#homepage_block_2-desktop',
				'homepage-block-3'   : '#homepage_block_3-desktop',
				'ros_column-block'   : '#column_block-desktop',
				'ros_leaderboard'    : '#leaderboard-bottom',
				'ros_button-1'       : '#button_1'
				
			},
			
			ros : {
				
				'custom-1' : '#custom_1',
				'button-2' : '#button_2'
				
			}
			
		}
		
	},
	
	methods = {
		
		init : function(options) {
			
			var settings = $.extend({}, defaults, options);
			
			if (settings.api && settings.section) {
				
				// Add '&cache=busted' to the end of the uri for testing newly added ads
				
				var uri = settings.api + (settings.parent ? settings.parent + ':' : '') + settings.section + '/' + (settings.page ? settings.page + '/' : '') + '?callback=?';
				
				if ($.jsonp) {
					
					/**
					 * Use @jaubourg's jQuery-JSONP plugin.
					 *
					 * @see rgne.ws/OEYxY2
					 */
					
					$.jsonp({
						url : uri,
						cache : true,
						success : function (json) {
							success(settings, json);
						}
					});
					
				} else {
					
					/**
					 * Use jQuery's $.getJSON.
					 *
					 * @see rgne.ws/S7EsQY
					 */
					
					$.getJSON(uri, function (json) {
						success(settings, json);
					});
					
				}
				
			} else {
				
				console.warn('Options "api" and "section" are requried.');
				
			}
			
		}
		
	},
	
	success = function(settings, json) {
		
		if (window.oMQ) {
			
			var flag = 1;
			
			window.oMQ.init(
				
				[
					
					{
						context : ['alpha', 'bravo'],
						call_for_each_context : false,
						match : function() {
							
							// For >> TEST << Purposes:
							console.log('FLAG: ' + flag);
							
							if (flag <= 2){
								
								$.each(json.target, function(key, target) {
									
									ad_code(settings, 'mobile', target, flag);
									
								});
								
							}
							
							flag++;
							
						}
					},
					
					{
						context : ['charlie','delta'],
						call_for_each_context : false,
						match : function() {
							
							// For >> TEST << Purposes:
							console.log('FLAG: ' + flag);
							
							if (flag <= 2){
								
								$.each(json.target, function(key, target) {
									
									ad_code(settings, 'desktop', target, flag);
									
								});
								
							}
							
							flag++;
							
						}
					}
					
				]
				
			);
			
		} else {
			
			console.warn('The onmediaquery library is not defined.');
			
		}
		
	},
	
	ad_code = function(settings, breakpoint, target, flag) {
		
		// For >> TEST << Purposes:
		console.log('BREAKPOINT: ' + breakpoint + ' | target name: ' + target.slug);
		
		$.each(target.ad_group[0].ad, function(key, value) {
			
			var ad_unit = '';
			
			if (target.slug === 'ros'){
				
				// ROS:
				
				ad_unit = ((flag === 1) && ((value.ad_type[0].slug === 'custom-1') || (value.ad_type[0].slug === 'button-2'))) ? $(settings.units.ros[value.ad_type[0].slug]) : $(settings.units[breakpoint]['ros_' + value.ad_type[0].slug]);
				
			} else {
				
				// Normal:
				
				ad_unit = $(settings.units[breakpoint][value.ad_type[0].slug]);
				
			}
			
			if ((typeof ad_unit !== 'undefined') && ad_unit.length) {
				
				var open = '',
				close    = '';
				//head   = ''; // See below.
				
				switch (value.ad_type[0].tag_type) {
					
					case '<iframe>':
						
						open  = '<iframe src="http://ox-d.registerguard.com/w/1.0/afr?auid=';
						close = '&cb=' + settings.cb + '"' + 'width="' + value.ad_type[0].width + '" height="' + value.ad_type[0].height + '" frameBorder="0" frameSpacing="0" scrolling="no"><\/iframe>';
						
						break;
					
					case '<script>':
						
						// This needs more work.
						/*
						head  = '<script src="http://ox-d.registerguard.com/w/1.0/jstag"></script><script>var OX=OX();OX.addPage("' + target.ad_group[0].aug_id + '");OX.fetchAds();<\/script>';
						open  = '<script>OX.showAdUnit("';
						close = '");<\/script>';
						*/
						
						break;
					
					case '<img>':
						
						open  = '<img src="http://ox-d.registerguard.com/w/1.0/ai?auid=';
						close = '&cb=' + settings.cb + '"' + '>';
						
						break;
					
					default:
						
						// IBID.
						open  = '<iframe src="http://ox-d.registerguard.com/w/1.0/afr?auid=';
						close = '&cb=' + settings.cb + '"' + 'width="' + value.ad_type[0].width + '" height="' + value.ad_type[0].height + '" frameBorder="0" frameSpacing="0" scrolling="no"><\/iframe>';
					
				}
				
				ad_unit.html(open + value.id + close);
				
				// For >> TEST << Purposes:
				console.log(target.slug, ' | ', value.ad_type[0].name, ' | ', value.ad_type[0].width, 'x', value.ad_type[0].height, ' | ', value.id);
				
			}
			
		});
		
	};
	
	$.ad_manager = function(method) {
		
		if (methods[method]) {
			
			return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
			
		} else if ((typeof method === 'object') || ( ! method)) {
			
			return methods.init.apply(this, arguments);
			
		} else {
			
			$.error('Method ' + method + ' does not exist on jQuery.ad_manager.');
			
		}
		
	};
	
}(jQuery, window, document));