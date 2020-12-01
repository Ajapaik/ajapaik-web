from collections import defaultdict

_styleConstraints = defaultdict(lambda: None)
_styleConstraints[
    "ep"
] = "▁sa ▁Sa ▁SA ▁sina ▁su ▁Su ▁sinu ▁Sinu ▁sul ▁Sul ▁sulle ▁sinuga ▁arvad ▁tahad ▁oled ▁soovid ▁du ▁dir ▁dich ▁dein ▁deine ▁deinen ▁deiner ▁deines ▁du ▁dir ▁dich ▁dein ▁deine ▁deinen ▁deiner ▁deines".split(
    " "
)
_styleConstraints[
    "ep"
] += "▁ты ▁Ты ▁тебя ▁тебе ▁Тебе ▁тобой ▁твой ▁твоё ▁твоему ▁твоим ▁твои".split(" ")
_styleConstraints["ep"] += "▁tu ▁Tu ▁tev ▁tevi".split(" ")

_styleConstraints[
    "os"
] = "▁te ▁Te ▁teie ▁teid ▁teile ▁Teile ▁teil ▁Teil ▁teilt ▁Teilt ▁Sie ▁Ihne ▁Ihnen ▁Ihner ▁Ihnes ▁Ihn".split(
    " "
)
_styleConstraints["os"] += "▁sir ▁Sir ▁ser ▁Ser".split(" ")
_styleConstraints["os"] += "▁сэр".split(" ")
_styleConstraints["os"] += "▁söör".split(" ")
_styleConstraints[
    "os"
] += "▁вы ▁Вы ▁вас ▁Вас ▁вам ▁Вам ▁вами ▁ваш ▁Ваш ▁ваши ▁вашего".split(" ")
_styleConstraints["os"] += "▁jūs ▁Jūs ▁jūsu ▁jums ▁Jums".split(" ")


def getPolitenessConstraints():
    return _styleConstraints
