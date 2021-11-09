from globals import client, db
from setting_helper import get_setting

def construct_drivers_page(guild, role):
    base = """
[column parallax_bg="disabled" parallax_bg_inertia="-0.2" extended="" extended_padding="1" background_color="" background_image="" background_repeat="" background_position="" background_size="auto" background_attachment="" hide_bg_lowres="" background_video="" vertical_padding_top="0" vertical_padding_bottom="0" more_link="" more_text="" left_border="transparent" class="" id="" title="" title_type="single" animation="none" width="1/1" last="true"]

[column_1 width="1/1" last="true" title="" title_type="single" animation="none" implicit="true"]
<img class=" wp-image-28760 aligncenter" src="https://m-e-t.org/wp-content/uploads/2021/03/b546ede2-5d5a-4da5-96c8-9c6ee2bef23f-300x240.jpg" alt="" width="515" height="412">
[/column_1]

[text_divider type="single"]
[M-E-T] Gründer
[/text_divider]

[column_1 width="1/3" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Silverado1985" position="Gründer / Kontor" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[column_1 width="1/3" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Schemi" position="Gründer Personalabteilung" url="/" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[column_1 width="1/3" last="true" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Bergbauer1950" position="Gründer / Kontor" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[text_divider type="single"]
[M-E-T] Abteilungsleiter
[/text_divider]

[column_1 width="1/6" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Wurstbrot" position="Personalabteilung" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[column_1 width="1/6" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="InDance2018" position="Event" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[column_1 width="1/6" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Sascha M" position="Sozialmedia" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[column_1 width="1/6" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Winsener.61" position="Abrechner" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[column_1 width="1/6" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Ehgner" position="Discord" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[column_1 width="1/6" last="true" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="Trucker Benni" position="ETS / ATS Experte" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]

[text_divider type="single"]
[M-E-T] Fahrer
[/text_divider]

///drivers///
[/column]
           """

    driver = """
[column_1 width="1/5" last="%s" title="undefined" title_type="undefined" animation="none" implicit="true"]
[team_member name="%s" position="Fahrer" url="" email="" phone="" picture="https://m-e-t.org/wp-content/uploads/2019/03/unknown.jpg" googleplus="/" linkedin="" facebook="/" twitter="/" youtube="/" instagram="/" dribble="/" vimeo="/"][/team_member]
[/column_1]
    """
    drivers = []
    i = 1
    for member in role.members:
        if i == 5:
            last = "true"
            i = 0
        else:
            last = "false"
        drivers.append(driver % (last, member.name))
        i += 1

    return base.replace("///drivers///", "\n".join(drivers))

@client.event
async def on_ready():
    print("Bot gestartet!")

@client.event
async def on_member_update(before, after):
    if before.roles == after.roles:
        return

    driver_role = int(get_setting("fahrer-rolle", db)[3:-1])
    if bool(driver_role in [role.id for role in before.roles]) ^ bool(driver_role in [role.id for role in after.roles]):
        role = before.guild.get_role(driver_role)
        page = construct_drivers_page(before.guild.id, role)
        print(page)
