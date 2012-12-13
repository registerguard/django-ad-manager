#!/usr/bin/python

import csv
import sys
from django.template.defaultfilters import slugify

from ad_manager.models import Ad, AdGroup, AdType, PageType, TagType, Target

def main(filename):
    reader = csv.reader(open(filename, 'rb'))
    # Skip first row, assuming it's the column name ... 
    reader.next()
    
    (site_section, site_subsection, location_type, ad_unit, ad_unit_size, ad_unit_group, ad_unit_group_id, ad_unit_name, ad_unit_id, full_script) = ('', '', '', '', '', '', '', '', '', '',)
    for row in reader:
        if any(row):
            # Get values of current row
            # ['NEWS', 'Homepage', 'Section', 'Leaderboard', '728 x 90', 'NEWS | Homepage | Section', '13785', 'NEWS | Homepage | Section | Leaderboard | 728 x 90', '304099']
            (current_site_section, current_site_subsection, current_location_type, current_ad_unit, current_ad_unit_size, current_ad_unit_group, current_ad_unit_group_id, current_ad_unit_name, current_ad_unit_id,) = row
            if current_site_section:
                site_section = current_site_section
            if current_site_subsection:
                site_subsection = current_site_subsection
            if current_location_type:
                location_type = current_location_type
            if current_ad_unit:
                ad_unit = current_ad_unit
            if current_ad_unit_size:
                ad_unit_size = current_ad_unit_size
            if current_ad_unit_group:
                ad_unit_group = current_ad_unit_group
            if current_ad_unit_group_id:
                ad_unit_group_id = current_ad_unit_group_id
            if current_ad_unit_name:
                ad_unit_name = current_ad_unit_name
            if current_ad_unit_id:
                ad_unit_id = current_ad_unit_id
                
            print '"{:<12s}" "{:<17s}" "{:<7s}" "{:<18s}" "{:<9s}" "{:<38s}" "{:<5s}" "{:<71s}" "{:<s}" "{:<s}"'.format(site_section, site_subsection, location_type, ad_unit, ad_unit_size, ad_unit_group, ad_unit_group_id, ad_unit_name, ad_unit_id, full_script)
            
            tag_type, tag_type_created = TagType.objects.get_or_create(name='<iframe>')
            ad_type, ad_type_created = AdType.objects.get_or_create(name=ad_unit, width=ad_unit_size.split(' x ')[0], 
                defaults = {'height': ad_unit_size.split(' x ')[1], 'tag_type': tag_type,}
            )
            print 'location_type::', '"', location_type, '"'
            page_type, page_type_created = PageType.objects.get_or_create(name=location_type, slug=slugify(location_type))
            subsection, subsection_created = Target.objects.get_or_create(name=site_subsection)
            if subsection_created and site_section:
                section, section_created = Target.objects.get_or_create(name=site_section)
                subsection.parent = section
                subsection.save()
            ad_group, ad_group_created = AdGroup.objects.get_or_create(aug_id=ad_unit_group_id, 
                defaults = {'page_type': page_type, 'target': subsection}
            )
            ad, ad_created = Ad.objects.get_or_create(ad_id=ad_unit_id, 
                defaults = {'ad_type': ad_type, 'ad_group': ad_group}
            )
            
        else:
            print 'Row of nothingness', row

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        print "Please supply the name of a .csv file to import. Thanks."
        sys.exit()
    main(filename)
